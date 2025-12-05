import subprocess

values = [19, 21, 32, 65, 69]

for v in values:
    nXX = f"{v:02d}"  # zero-pad to match nXX → n019, n021, etc.
    
    inpath = f"/datalake/NS9560K/rosief/noresm_beta06_crujra_i2000_ppe_v1_n{nXX}/lnd/hist/"
    inpath = f"/datalake/NS9560K/rosief/noresm_beta06_cplhist_2000_ppe_v1_n{nXX}/lnd/hist/"
    inpath = f"/datalake/NS9560K/rosief/noresm_beta06_cplhist_ppe_v1_n{nXX}/lnd/hist/"
#    inpath = f"/datalake/NS9560K/noresm3/cases/coupled_ppe.20251108/ensemble_member.0{nXX}/lnd/hist/"
    
    cmd = [
        "python",
        "run_diagnostic_full_from_terminal.py",
        inpath,
        "outpath=/datalake/NS9560K/www/diagnostics/noresm/rosief",
        "pamfile=json_file_library/long_diags.json",
        "weight=/datalake/NS9560K/diagnostics/land_xesmf_diag_data/map_ne16pg3_to_1.9x2.5_nomask_scripgrids_c250425.nc",
        "mute_trend=True",
	"mute_maps=False"
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
