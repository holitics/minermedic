routes = {
  '{"command": "stats"}':

    {"STATUS": [{"STATUS": "S", "When": 1481670954, "Code": 70, "Msg": "CGMiner stats", "Description": "cgminer 4.10.0"}],
      "STATS": [{"STATS": 0, "ID": "AV70", "Elapsed": 181, "Calls": 0, "Wait": 0.0, "Max": 0.0, "Min": 99999999.0,
                 "MM ID1": "Ver[7411706-3162860] DNA[013cae6bfb1bb6c6] Elapsed[183] MW[2024 2024 2024 2002] LW[8074] MH[3 0 3 4] HW[10] DH[0.000%] Temp[38] TMax[93] Fan[4110] FanR[48%] Vi[1215 1215 1211 1210] Vo[4461 4447 4438 4438] GHSmm[7078.84] WU[88583.15] Freq[628.45] PG[15] Led[0] MW0[6 3 8 7 5 10 4 5 6 7 12 4 7 9 6 11 11 9 11 9 7 4] MW1[3 5 9 8 7 4 4 4 6 5 9 3 8 4 8 8 7 5 6 8 4 4] MW2[12 7 3 4 5 4 5 2 6 6 11 6 6 6 7 5 5 9 4 6 6 5] MW3[5 3 11 5 5 5 4 6 8 6 3 7 3 8 4 9 4 7 7 3 5 3] TA[88] ECHU[16 0 0 0] ECMM[0] FM[1] CRC[0 0 0 0] PAIRS[0 0 0] PVT_T[21-76/1-88/83 1-80/11-92/84 21-82/12-93/83 1-82/10-93/87]",
                 "MM Count": 1, "Smart Speed": 1, "Connecter": "AUC", "AUC VER": "AUC-20151208", "AUC I2C Speed": 400000,
                 "AUC I2C XDelay": 19200, "AUC Sensor": 13999, "AUC Temperature": 32.97, "Connection Overloaded": False,
                 "Voltage Offset": 0, "Nonce Mask": 29, "USB Pipe": "0", "USB Delay": "r0 0.000000 w0 0.000000", "USB tmo": "0 0"},
                {"STATS": 1, "ID": "POOL0", "Elapsed": 181, "Calls": 0, "Wait": 0.0, "Max": 0.0, "Min": 99999999.0,
                 "Pool Calls": 0, "Pool Attempts": 0, "Pool Wait": 0.0, "Pool Max": 0.0, "Pool Min": 99999999.0,
                 "Pool Av": 0.0, "Work Had Roll Time": False, "Work Can Roll": False, "Work Had Expire": False,
                 "Work Roll Time": 0, "Work Diff": 4096.0, "Min Diff": 4096.0, "Max Diff": 4096.0, "Min Diff Count": 571,
                 "Max Diff Count": 571, "Times Sent": 65, "Bytes Sent": 7587, "Times Recv": 75, "Bytes Recv": 14343,
                 "Net Bytes Sent": 7587, "Net Bytes Recv": 14343},
                {"STATS": 2, "ID": "POOL1", "Elapsed": 181, "Calls": 0, "Wait": 0.0, "Max": 0.0, "Min": 99999999.0,
                 "Pool Calls": 0, "Pool Attempts": 0, "Pool Wait": 0.0, "Pool Max": 0.0, "Pool Min": 99999999.0,
                 "Pool Av": 0.0, "Work Had Roll Time": False, "Work Can Roll": False, "Work Had Expire": False,
                 "Work Roll Time": 0, "Work Diff": 0.0, "Min Diff": 0.0, "Max Diff": 0.0, "Min Diff Count": 0,
                 "Max Diff Count": 0, "Times Sent": 2, "Bytes Sent": 145, "Times Recv": 5, "Bytes Recv": 1544,
                 "Net Bytes Sent": 145, "Net Bytes Recv": 1544},
                {"STATS": 3, "ID": "POOL2", "Elapsed": 181, "Calls": 0, "Wait": 0.0, "Max": 0.0, "Min": 99999999.0,
                 "Pool Calls": 0, "Pool Attempts": 0, "Pool Wait": 0.0, "Pool Max": 0.0, "Pool Min": 99999999.0,
                 "Pool Av": 0.0, "Work Had Roll Time": False, "Work Can Roll": False, "Work Had Expire": False,
                 "Work Roll Time": 0, "Work Diff": 0.0, "Min Diff": 0.0, "Max Diff": 0.0, "Min Diff Count": 0,
                 "Max Diff Count": 0, "Times Sent": 2, "Bytes Sent": 145, "Times Recv": 5, "Bytes Recv": 1544,
                 "Net Bytes Sent": 145, "Net Bytes Recv": 1544}], "id": 1},

  '{"command": "devs"}':

    {"STATUS": [{"STATUS": "S", "When": 1481670955, "Code": 9, "Msg": "1 ASC(s)", "Description": "cgminer 4.10.0"}],
     "DEVS": [{"ASC": 0, "Name": "AV7", "ID": 0, "Enabled": "Y", "Status": "Alive", "Temperature": 32.97,
               "MHS av": 6415043.46, "MHS 5s": 5583536.75, "MHS 1m": 6057850.56, "MHS 5m": 2876993.43,
               "MHS 15m": 1156269.52, "Accepted": 63, "Rejected": 1, "Hardware Errors": 10, "Utility": 21.11,
               "Last Share Pool": 0, "Last Share Time": 1481670954, "Total MH": 1148491159.0, "Diff1 Work": 272000,
               "Difficulty Accepted": 258048.0, "Difficulty Rejected": 4096.0, "Last Share Difficulty": 4096.0,
               "No Device": False, "Last Valid Work": 1481670955, "Device Hardware%": 0.0037,
               "Device Rejected%": 1.5059, "Device Elapsed": 179}], "id": 1},

  '{"command": "summary"}' :

    {"STATUS": [{"STATUS": "S", "When": 1481670956, "Code": 11, "Msg": "Summary", "Description": "cgminer 4.10.0"}],
     "SUMMARY": [{"Elapsed": 184, "MHS av": 6325487.11, "MHS 5s": 7031761.33, "MHS 1m": 6188400.86, "MHS 5m": 2919529.44,
                  "MHS 15m": 1173385.08, "Found Blocks": 0, "Getworks": 12, "Accepted": 65, "Rejected": 1,
                  "Hardware Errors": 10, "Utility": 21.16, "Discarded": 100, "Stale": 0, "Get Failures": 0,
                  "Local Work": 1208, "Remote Failures": 0, "Network Blocks": 2, "Total MH": 1165671025.0,
                  "Work Utility": 89699.67, "Difficulty Accepted": 266240.0, "Difficulty Rejected": 4096.0,
                  "Difficulty Stale": 0.0, "Best Share": 370743, "Device Hardware%": 0.0036, "Device Rejected%": 1.4868,
                  "Pool Rejected%": 1.5152, "Pool Stale%": 0.0, "Last getwork": 1481670954}], "id": 1},


  '{"command": "pools"}' :

    {"STATUS": [{"STATUS": "S", "When": 1481670958, "Code": 7, "Msg": "3 Pool(s)", "Description": "cgminer 4.10.0"}],
     "POOLS": [
       {"POOL": 0, "URL": "stratum+tcp://btc.viabtc.com:3333", "Status": "Alive", "Priority": 0, "Quota": 1,
                "Long Poll": "N", "Getworks": 10, "Accepted": 65, "Rejected": 1, "Works": 557, "Discarded": 100,
                "Stale": 0, "Get Failures": 0, "Remote Failures": 0, "User": "franklinminer.canaan1",
                "Last Share Time": 1481670956, "Diff1 Shares": 277000, "Proxy Type": "", "Proxy": "",
                "Difficulty Accepted": 266240.0, "Difficulty Rejected": 4096.0, "Difficulty Stale": 0.0,
                "Last Share Difficulty": 4096.0, "Work Difficulty": 4096.0, "Has Stratum": True, "Stratum Active": True,
                "Stratum URL": "btc.viabtc.com", "Stratum Difficulty": 4096.0, "Has GBT": False, "Best Share": 370743,
                "Pool Rejected%": 1.5152, "Pool Stale%": 0.0, "Bad Work": 1, "Current Block Height": 587796,
                "Current Block Version": 536870912},
       {"POOL": 1, "URL": "stratum+tcp://stratum80.kano.is:80", "Status": "Alive", "Priority": 1, "Quota": 1,
                "Long Poll": "N", "Getworks": 1, "Accepted": 0, "Rejected": 0, "Works": 0, "Discarded": 0,
                "Stale": 0, "Get Failures": 0, "Remote Failures": 0, "User": "canaan.80", "Last Share Time": 0,
                "Diff1 Shares": 0, "Proxy Type": "", "Proxy": "", "Difficulty Accepted": 0.0, "Difficulty Rejected": 0.0,
                "Difficulty Stale": 0.0, "Last Share Difficulty": 0.0, "Work Difficulty": 0.0, "Has Stratum": True,
                "Stratum Active": False, "Stratum URL": "", "Stratum Difficulty": 0.0, "Has GBT": False, "Best Share": 0,
                "Pool Rejected%": 0.0, "Pool Stale%": 0.0, "Bad Work": 0, "Current Block Height": 0, "Current Block Version": 536870912},
       {"POOL": 2, "URL": "stratum+tcp://stratum81.kano.is:81", "Status": "Alive", "Priority": 2, "Quota": 1,
                "Long Poll": "N", "Getworks": 1, "Accepted": 0, "Rejected": 0, "Works": 0, "Discarded": 0, "Stale": 0,
                "Get Failures": 0, "Remote Failures": 0, "User": "canaan.81", "Last Share Time": 0, "Diff1 Shares": 0,
                "Proxy Type": "", "Proxy": "", "Difficulty Accepted": 0.0, "Difficulty Rejected": 0.0,
                "Difficulty Stale": 0.0, "Last Share Difficulty": 0.0, "Work Difficulty": 0.0, "Has Stratum": True,
                "Stratum Active": False, "Stratum URL": "", "Stratum Difficulty": 0.0, "Has GBT": False, "Best Share": 0,
                "Pool Rejected%": 0.0, "Pool Stale%": 0.0, "Bad Work": 0, "Current Block Height": 0, "Current Block Version": 536870912}], "id": 1}
}