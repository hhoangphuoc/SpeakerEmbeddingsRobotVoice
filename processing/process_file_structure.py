## rename the files in the current directory with the given format: <speaker_id>_<description>.wav


import os
import sys
from os.path import join as opj

def rename_files(path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.wav'):
            filename, ext = file.split('.')

            spk_id = ""
            description = ""

            splitter = filename.split('_')
            if len(splitter) == 3:
                # final case after 2 times processes - merge name of splitter[1] and splitter[2]
                new_filename = f'{splitter[0]}_{splitter[1]}{splitter[2]}' + '.' + ext

            elif len(splitter) == 2 and splitter[2] == "":
                # handling the case where the filename is written in camel case
                # e.g. ABeepProcessing_.wav to A_BeepProcessing_.wav
                new_filename = filename[0] + '_' + filename[1:] + '.' + ext
                
            else:
                if splitter[0] == "BEST":
                    spk_id = splitter[1]
                else:
                    spk_id = splitter[0]
                description = "_".join(splitter[1:])
                new_filename = f'{spk_id}_{description}' + '.' + ext

            os.rename(opj(path, file), opj(path, new_filename))

# mapping sound id to speaker id
# sid_to_spk = {
#     '1': ['1111', '1112', '1113', '1114', '1115', '1116', '1117', '1118', '1119', '1120', '1121', '1122', '1123', '1124', '1125', '1126', '1127', '1128', '1129', '1130', '1131', '1132', '1133', '1134', '1135', '1136', '1137', '1138', '1139'],
#     '2': ['1140', '1141', '1142', '1143', '1144', '1145', '1146'],
#     '3': ['1147', '1148', '1149', '1150', '1151', '1152', '1153', '1154', '1155', '1156', '1157', '1158', '1159', '1160', '1161', '1162', '1163', '1164', '1165', '1166', '1167', '1168', '1169', '1170', '1171', '1172', '1173', '1174'],
#     '4': ['1175', '1176', '1177', '1178', '1179', '1180', '1181', '1182', '1183', '1184', '1185', '1186', '1187', '1188', '1189', '1190', '1191', '1192', '1193', '1194', '1195', '1196', '1197', '1198', '1199', '1200', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209', '1210', '1211', '1212', '1213', '1214', '1215', '1216', '1217', '1218', '1219', '1220', '1221', '1222', '1223', '1224', '1225', '1226', '1227', '1228', '1229', '1230', '1231', '1232', '1233', '1234', '1235', '1236', '1237', '1238', '1239', '1240', '1241', '1242', '1243', '1244', '1245', '1246', '1247', '1248', '1249', '1250', '1251', '1252', '1253', '1254', '1255', '1256', '1257', '1258', '1259', '1260', '1261', '1262', '1263', '1264', '1265', '1266', '1267', '1268', '1269', '1270', '1271', '1272', '1273', '1274', '1275', '1276', '1277', '1278', '1279', '1280', '1281', '1282', '1283', '1284', '1285', '1286', '1287', '1288', '1289', '1290', '1291', '1292', '1293', '1294', '1295', '1296', '1297', '1298', '1299', '1300', '1301', '1302', '1303', '1304', '1305', '1306', '1307', '1308', '1309', '1310', '1311', '1312', '1313', '1314', '1315', '1316', '1317', '1318', '1319', '1320', '1321', '1322', '1323', '1324', '1325', '1326', '1327', '1328', '1329', '1330', '1331', '1332', '1333', '1334', '1335', '1336', '1337', '1338', '1339', '1340', '1341', '1342', '1343', '1344', '1345', '1346', '1347', '1348', '1349', '1350', '1351', '1352', '1353', '1354', '1355', '1356', '1357', '1358', '1359', '1360', '1361', '1362', '1363', '1364', '1365', '1366', '1367', '1368', '1369', '1370', '1371', '1372', '1373', '1374', '1375', '1376', '1377', '1378', '1379', '1380', '1381', '1382', '1383', '1384', '1385', '1386', '1387', '1388', '1389', '1390', '1391', '1392', '1393', '1394', '1395', '1396', '1397', '1398', '1399', '1400', '1401', '1402', '1403', '1404', '1405', '1406', '1407', '1408', '1409', '1410', '1411', '1412', '1413', '1414', '1415', '1416', '1417', '1418', '1419', '1420', '1421', '1422', '142
def get_spk_from_range(from_spk, to_spk):
    spk_list = []
    for i in range(from_spk, to_spk + 1):
        spk_list.append(str(i))
    return spk_list

def generate_speakers_mapping():
    # generate the mapping from sound id to speaker id
    sid_to_spk = {
        'spk_1': get_spk_from_range(1111, 1139),
        'spk_2': get_spk_from_range(1140, 1146),
        'spk_3': get_spk_from_range(1147, 1174),
        'spk_4': get_spk_from_range(1175, 1204),
        'spk_5': get_spk_from_range(1205, 1232),
        'spk_6': get_spk_from_range(1233, 1262),
        'spk_11': get_spk_from_range(1263, 1290),
        'spk_12': get_spk_from_range(1321, 1350),
        'spk_13': get_spk_from_range(1351, 1363),
        'spk_14': 'A',
        'spk_15': 'B',
        'spk_16': 'C',
        'spk_17': 'D',
        'spk_18': 'E',
        'spk_19': 'F',
        'spk_20': 'G',
        'spk_21': 'H',
        'spk_22': 'I',
        'spk_23': 'J',
        'spk_24': 'K',
        'spk_25': 'L',
        'spk_26': 'M',
        'spk_27': 'R2D2',
        'spk_28': 'WALL-E',
    }
    return sid_to_spk

def seperate_speakers(path):
    # function that seperate the speakers in current directory into different folder
    # by the speaker id, the speaker id is the first part of the filename
    speakers_mapping = generate_speakers_mapping()
    files = os.listdir(path)
    temp_folder_name = ''
    for file in files:
        if file.endswith('.wav'):
            filename, ext = file.split('.')
            spk_id = filename.split('_')[0] # eg: 1111, A, B, R2D2

            for key, value in speakers_mapping.items():
                if spk_id in value:
                    if not os.path.exists(opj(path, key)):
                        os.makedirs(opj(path, key))
                        temp_folder_name = key
            # move the file to the corresponding folder
            if not os.path.exists(opj(path, temp_folder_name, file)):
                os.rename(opj(path, file), opj(path, temp_folder_name, file))

            # if spk_id in speakers_mapping:
            #     if not os.path.exists(opj(path, speakers_mapping[spk_id])):
            #         os.makedirs(opj(path, speakers_mapping[spk_id]))
            #     os.rename(opj(path, file), opj(path, speakers_mapping[spk_id], file))


if __name__ == '__main__':
    path = opj(os.getcwd(), 'data', 'Phuoc', 'input')
    # rename_files(path)
    seperate_speakers(path)