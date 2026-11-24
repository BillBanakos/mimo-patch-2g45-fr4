import json, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'results', 'res_L28.00_W37.23_y8.50_ff.json')))
f = np.array(d['f'])/1e9
S11 = np.array([complex(*z) for z in d['S11']]); S21 = np.array([complex(*z) for z in d['S21']])
s11 = 20*np.log10(abs(S11)); s21 = 20*np.log10(abs(S21))
bw = f[s11 < -10]; print('-10dB BW %.3f-%.3f GHz (%.0f MHz)' % (bw.min(), bw.max(), (bw.max()-bw.min())*1e3))
i = np.argmin(abs(f-2.45)); print('@2.45: S11 %.1f S21 %.1f' % (s11[i], s21[i]), 'worst S21 in band %.1f' % s21[(f>=2.4)&(f<=2.4835)].max())
# far-field ECC, port2 pattern = mirror x->-x of port1
th = np.deg2rad(d['th3']); ph = np.array(d['ph3'])
Et = np.array(d['Eth_re'])+1j*np.array(d['Eth_im']); Ep = np.array(d['Eph_re'])+1j*np.array(d['Eph_im'])
# arrays are (phi, theta) or (theta, phi)?
if Et.shape[0] != len(ph): Et, Ep = Et.T, Ep.T
idx = [list(ph).index((180-p) % 360) for p in ph]
Et2, Ep2 = Et[idx], -Ep[idx]
dO = np.sin(th)[None, :]
num = abs(np.sum((Et*np.conj(Et2)+Ep*np.conj(Ep2))*dO))**2
den = np.sum((abs(Et)**2+abs(Ep)**2)*dO)*np.sum((abs(Et2)**2+abs(Ep2)**2)*dO)
print('ECC far-field @2.45 = %.2e' % (num/den))
eccs = abs(np.conj(S11)*S21+np.conj(S21)*S11)**2/((1-abs(S11)**2-abs(S21)**2)**2)
print('ECC S-param @2.45 = %.2e' % eccs[i])
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(f, s11, label='S11 = S22'); ax[0].plot(f, s21, label='S21')
ax[0].axvspan(2.4, 2.4835, color='0.9', label='WiFi 2.4 GHz band'); ax[0].axhline(-10, ls='--', c='k', lw=.8)
ax[0].set(xlabel='Frequency (GHz)', ylabel='dB', title='S-parameters (openEMS FDTD)', ylim=(-50, 0)); ax[0].legend(); ax[0].grid(alpha=.3)
t = np.deg2rad(d['theta']); ax[1].remove(); a = fig.add_subplot(1, 2, 2, projection='polar')
G = 10*np.log10(d['Dmax']*d['eff'])
for k, nm in enumerate(['phi=0 (xz, H-plane)', 'phi=90 (yz, E-plane)']):
    En = np.array(d['E_norm'][k]); a.plot(t, np.maximum(20*np.log10(En/En.max())+G, -30), label=nm)
a.set_theta_zero_location('N'); a.set_theta_direction(-1); a.set_rlim(-30, 10)
a.set_title('Gain pattern port 1 @2.45 GHz (dBi)'); a.legend(loc='lower left', fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(HERE, '..', 'docs', 'results.png'), dpi=130)
