from polymer_kitchen.parser import Parser
from polymer_kitchen.build import Amorphous_builder
import jax
import jax.numpy as jnp
import numpy as onp
from itertools import combinations
import random
parser = Parser('recipe')

am = Amorphous_builder(parser)
am.init()
box = parser.box_size[0]

p = am.position
n = am.stats['total']
dx = 1e-3/5

f = open('traj', 'w') 
atom_type_dic = am.index_to_type
atom_type_index = []

pairs = [comb for comb in combinations([i for i in range(n)], 2)]
i_r1 = jnp.array([i[0] for i in pairs])
i_r2 = jnp.array([i[1] for i in pairs])

for i in range(n):
    for t in atom_type_dic:
        if i in atom_type_dic[t]:
            atom_type_index.append(t)

print(atom_type_index)
atom_type = []
for i in atom_type_index:
    if i == 1:
        atom_type.append('H')
    elif i == 2:
        atom_type.append('O')
    else:
        atom_type.append('C')


def write_traj(p):
    f.write(f"{am.stats['total']}\n\n")
    for idx, a in enumerate(p):
        f.write(f'{atom_type[idx]}    {a[0]}    {a[1]}    0\n')

@jax.jit
def check_periodic_boundary(r):
    r_b = r + box
    r_s = r - box
    n = r.shape[1]
    new = []
    for i in range(n):
        fst = jnp.where(r[:,i] < -box/2, r_b[:,i], r[:,i])
        scd = jnp.where(fst > box/2, r_s[:,i], fst)
        new.append(scd)
    return jnp.array(new).T

@jax.jit
def energy_angle(a1, a2, a3, theta, intensity):
    r1 = a1 - a2
    r2 = a3 - a2
    r1 = check_periodic_boundary(r1)
    r2 = check_periodic_boundary(r2)
    r1_dot_r2 = jnp.einsum('ij,ij->i',r1, r2)
    r1_s = jnp.sqrt(jnp.sum(r1**2, axis=1))
    r2_s = jnp.sqrt(jnp.sum(r2**2, axis=1))
    angle = jnp.arccos(r1_dot_r2/(r1_s * r2_s + dx*random.random()))/jnp.pi * 180
    return jnp.sum(intensity * (angle - theta)**2)

@jax.jit
def energy_bond(r1, r2, length, intensity):
    del_r = r1 - r2
    del_r = check_periodic_boundary(del_r)
    distance = jnp.sqrt(jnp.sum(del_r**2, axis=1))
    return jnp.sum(intensity * (distance - length)**2)

@jax.jit
def lj(r1, r2):
    del_r = r1 - r2
    del_r = check_periodic_boundary(del_r)
    distance = jnp.sqrt(jnp.sum(del_r**2, axis=1))
    return jnp.sum(distance**(-12) - distance**(-6))

def total_energy(p):
    U = 0
    for b in am.bonds:
        intensity = b.intensity
        length = b.length
        r1 = jnp.array(p[onp.array(am.bonds[b]['r1'])])
        r2 = jnp.array(p[onp.array(am.bonds[b]['r2'])])
        eng_bond = energy_bond(r1, r2, length, intensity)
        U += eng_bond

    for a in am.angles:
        intensity = a.intensity
        theta = a.theta
        a1 = jnp.array(p[onp.array(am.angles[a]['a1'])])
        a2 = jnp.array(p[onp.array(am.angles[a]['a2'])])
        a3 = jnp.array(p[onp.array(am.angles[a]['a3'])])
        eng_angle = energy_angle(a1, a2, a3, theta, intensity)
        U += eng_angle

    pairs = [comb for comb in combinations(p, 2)]
    lj_r1 = p[i_r1]
    lj_r2 = p[i_r2]
    U += lj(lj_r1, lj_r2)
    print(f"total energy = {U}")
    return U


grad_energy = jax.grad(total_energy)

#define Monte Carlo simulation to randomly swap the position of two atoms
l = [i for i in range(n)]

def MonteCarlo(p):
    p = onp.array(p)
    U = total_energy(p)
    for i in range(5000):
        U_old = U
        atom1, atom2 = random.sample(l, 2)
        p_new = p.copy()
        p_new[[atom1, atom2]] = p_new[[atom2, atom1]]
        U = total_energy(p_new)
        if U < U_old:
            p = p_new.copy()
        else:
            U = U_old
    return p



def MD(p):
    for i in range(100):
        p += -grad_energy(p) * dx
        p = check_periodic_boundary(p)
        write_traj(p)
    return p

for i in range(10):
    p = MonteCarlo(p)
    p = MD(p)

f.close()





