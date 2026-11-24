"""1x2 MIMO inset-fed patch, FR4 1.6 mm, 160x100 mm board, 2.45 GHz. openEMS FDTD.
usage: RES=30 python3 mimo.py L W y0 [ff]   (final: 28.0 37.23 8.5 ff)
RES = mesh cells per wavelength in FR4 (default 20; 30 used for final results)
"""
import os, sys, json, tempfile
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0

L   = float(sys.argv[1])          # patch resonant length (y)
W   = float(sys.argv[2])          # patch width (x)
y0  = float(sys.argv[3])          # inset depth
do_ff = len(sys.argv) > 4

f0, fc = 2.45e9, 1.0e9
er, tand, h = 4.4, 0.02, 1.6
BX, BY = 160.0, 100.0             # board
wf = 3.06                         # 50 ohm line
g  = 1.0                          # inset notch gap each side
dx = 40.0                         # patch centre x = +-dx (80 mm pitch)
yc = 10.0                         # patch centre y (board spans -50..50)
unit = 1e-3
RESDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')

sim = tempfile.mkdtemp(prefix='mimo_')
FDTD = openEMS(NrTS=60000, EndCriteria=1e-4)
FDTD.SetGaussExcite(f0, fc)
FDTD.SetBoundaryCond(['MUR'] * 6)
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(unit)

air = 40.0
SimBox = [BX + 2 * air, BY + 2 * air, 2 * air]
mesh.AddLine('x', [-SimBox[0] / 2, SimBox[0] / 2])
mesh.AddLine('y', [-SimBox[1] / 2, SimBox[1] / 2])
mesh.AddLine('z', [-SimBox[2] / 2 + h, SimBox[2] / 2])

sub = CSX.AddMaterial('FR4', epsilon=er, kappa=2 * np.pi * f0 * EPS0 * er * tand)
sub.AddBox([-BX / 2, -BY / 2, 0], [BX / 2, BY / 2, h], priority=0)
mesh.AddLine('z', np.linspace(0, h, 5))
mesh.AddLine('x', [-BX / 2, BX / 2]); mesh.AddLine('y', [-BY / 2, BY / 2])

gnd = CSX.AddMetal('gnd')
gnd.AddBox([-BX / 2, -BY / 2, 0], [BX / 2, BY / 2, 0], priority=10)
cu = CSX.AddMetal('patch')

ports = []
for i, s in enumerate([-1, 1]):
    xc = s * dx
    yb, yt = yc - L / 2, yc + L / 2
    xl, xr = xc - W / 2, xc + W / 2
    # patch with inset notch = patch minus two slots (build as 3 boxes)
    cu.AddBox([xl, yb + y0, h], [xr, yt, h], priority=10)                       # upper body
    cu.AddBox([xl, yb, h], [xc - wf / 2 - g, yb + y0, h], priority=10)          # left leg
    cu.AddBox([xc + wf / 2 + g, yb, h], [xr, yb + y0, h], priority=10)          # right leg
    cu.AddBox([xc - wf / 2, -BY / 2, h], [xc + wf / 2, yb + y0, h], priority=10) # feed line
    # mesh lines (thirds rule on metal edges)
    r = 0.4
    mesh.AddLine('x', [xl - r / 3, xl + 2 * r / 3, xr + r / 3, xr - 2 * r / 3,
                       xc - wf / 2 - r / 3, xc - wf / 2 + 2 * r / 3, xc + wf / 2 + r / 3, xc + wf / 2 - 2 * r / 3,
                       xc - wf / 2 - g, xc + wf / 2 + g, xc])
    mesh.AddLine('y', [yb - r / 3, yb + 2 * r / 3, yt + r / 3, yt - 2 * r / 3, yb + y0])
    p = FDTD.AddLumpedPort(i + 1, 50, [xc - wf / 2, -BY / 2, 0], [xc + wf / 2, -BY / 2 + 0.5, h],
                           'z', excite=1.0 if i == 0 else 0)
    ports.append(p)
mesh.AddLine('y', [-BY / 2 + 0.5])

mesh.SmoothMeshLines('all', C0 / (f0 + fc) / unit / float(os.environ.get("RES","20")) / np.sqrt(er), 1.4)
for d in 'xy':  # keep air coarser is automatic via smoothing
    pass

if do_ff:
    nf2ff = FDTD.CreateNF2FFBox()

FDTD.Run(sim, cleanup=True, verbose=0)

f = np.linspace(2.0e9, 2.9e9, 451)
for p in ports:
    p.CalcPort(sim, f)
S11 = ports[0].uf_ref / ports[0].uf_inc
S21 = ports[1].uf_ref / ports[0].uf_inc
out = dict(L=L, W=W, y0=y0, f=f.tolist(), S11=[[z.real, z.imag] for z in S11],
           S21=[[z.real, z.imag] for z in S21],
           Zin=[[z.real, z.imag] for z in (ports[0].uf_tot / ports[0].if_tot)],
           Pin=np.real(ports[0].P_acc).tolist())
if do_ff:
    i0 = np.argmin(np.abs(20 * np.log10(np.abs(S11))))
    fr = 2.45e9
    th = np.arange(-180, 181, 2.0); ph = [0, 90]
    res = nf2ff.CalcNF2FF(sim, fr, th, ph, center=[0, 0, 1e-3], outfile='cut.h5')
    th2 = np.arange(0, 181, 3.0); ph2 = np.arange(0, 361, 6.0)
    res3 = nf2ff.CalcNF2FF(sim, fr, th2, ph2, center=[0, 0, 1e-3], outfile='full.h5')
    Pacc = np.interp(fr, f, np.real(ports[0].P_acc))
    out.update(ff_f=fr, theta=th.tolist(),
               E_norm=[(res.E_norm[0][:, k]).tolist() for k in range(2)],
               Dmax=float(res.Dmax[0]), Prad=float(res.Prad[0]), Pacc=float(Pacc),
               eff=float(res.Prad[0] / Pacc),
               # complex far-field components for ECC (phi x theta)
               th3=th2.tolist(), ph3=ph2.tolist(),
               Eth_re=np.real(res3.E_theta[0]).tolist(), Eth_im=np.imag(res3.E_theta[0]).tolist(),
               Eph_re=np.real(res3.E_phi[0]).tolist(), Eph_im=np.imag(res3.E_phi[0]).tolist())
tag = f"L{L:.2f}_W{W:.2f}_y{y0:.2f}{'_ff' if do_ff else ''}"
os.makedirs(RESDIR, exist_ok=True)
json.dump(out, open(os.path.join(RESDIR, f'res_{tag}.json'), 'w'))
s = 20 * np.log10(np.abs(S11)); i0 = np.argmin(s)
print(f"{tag}: fres={f[i0]/1e9:.4f} GHz S11min={s[i0]:.1f} dB  S21@fres={20*np.log10(abs(S21[i0])):.1f} dB "
      f"Zin@fres={complex(out['Zin'][i0][0], out['Zin'][i0][1]):.1f}")
