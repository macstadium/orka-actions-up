# orka-actions-up

Run self-hosted, macOS workflows on MacStadium's Orka. 

## Overview
This action is intended to be paired with [`jeff-vincent/orka-actions-down@v1.0.0`](https://github.com/marketplace/actions/orka-actions-down) in order to pass iOS and macOS CI/CD jobs to ephemeral, self-hosted runners in [MacStadium's Orka](https://orkadocs.macstadium.com). 

orka-actions-up is responsible for spinning up a fresh macOS VM in Orka, which then registers itself as a self-hosted runner with the help of the agent resources housed and detailed in [`jeff-vincent/orka-actions-connect`](https://github.com/jeff-vincent/orka-actions-connect). 

Finally, as shown in the example below, [`jeff-vincent/orka-actions-down@v1.0.0`](https://github.com/marketplace/actions/orka-actions-down), tears down the ephemeral macOS, self-hosted runner.

## Example workflow

```
on:
  push:
    branches:
      - main

jobs:
  job1:
    runs-on: ubuntu-latest          # NOTE: both orka-actions-up and orka-actions-down run on `ubuntu-latest`
    steps:
    - name: Job 1
      id: job1
      uses: jeff-vincent/orka-actions-up@v1.1.1
      with:
        orkaUser: ${{ secrets.ORKA_USER }}
        orkaPass: ${{ secrets.ORKA_PASS }}
        orkaBaseImage: gha_bigsur_v3.img             # NOTE: this `.img` file is the agent that has been defined in Orka
        githubPat: ${{ secrets.GH_PAT }}             
        vpnUser: ${{ secrets.VPN_USER }}
        vpnPassword: ${{ secrets.VPN_PASSWORD }}
        vpnAddress: ${{ secrets.VPN_ADDRESS }}
        vpnServerCert: ${{ secrets.VPN_SERVER_CERT }}
        vcpuCount: 6
        coreCount: 6
    outputs:
      vm-name: ${{ steps.job1.outputs.vm-name }}
         
  job2:            # NOTE: this is where your macOS-based, GitHub Actions workflow will be executed.
    needs: job1     
    runs-on: [self-hosted, "${{ needs.job1.outputs.vm-name }}"]     # NOTE: this section of the workflow can contain any number of seperate jobs,
    steps:                                                          # but each must have this `runs-on` value.
    - name: Job 2
      id: job2
      run: |
        sw_vers
  job3:
    if: always()
    needs: [job1, job2]               # NOTE: all jobs you wish to run on the macOS instance, 
    runs-on: ubuntu-latest            # along with the `orka-actions-up` job, must be listed here.
    steps:
    - name: Job 3
      id: job3
      uses: jeff-vincent/orka-actions-down@v1.1.0
      with:
        orkaUser: ${{ secrets.ORKA_USER }}
        orkaPass: ${{ secrets.ORKA_PASS }}
        githubPat: ${{ secrets.GH_PAT }}
        vpnUser: ${{ secrets.VPN_USER }}
        vpnPassword: ${{ secrets.VPN_PASSWORD }}
        vpnAddress: ${{ secrets.VPN_ADDRESS }}
        vpnServerCert: ${{ secrets.VPN_SERVER_CERT }}
        vmName: ${{ needs.job1.outputs.vm-name }}
```

## job2 example output

```
Run sw_vers
  sw_vers
  shell: /bin/bash -e {0}
ProductName:	macOS
ProductVersion:	11.3
BuildVersion:	20E232
```
