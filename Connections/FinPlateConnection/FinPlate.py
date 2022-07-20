import logging

import yaml

from design_type.connection.fin_plate_connection import FinPlateConnection
from UI_DESIGN_PREFERENCE import DesignPreferences
from Common import *
class FinPlate(FinPlateConnection):
    def __init__(self, connectivity, ColumnSection, BeamSection, Material,**kwargs):
        super().__init__()
        self.Connectivity = connectivity
        self.design_dict={}
        self.design_dict['Connectivity'] = connectivity
        self.ColumnSection = ColumnSection
        self.BeamSection = BeamSection
        self.material = Material
        self.design_dict['Member.Supporting_Section.Designation'] = self.ColumnSection
        self.design_dict['Member.Supported_Section.Designation']= self.BeamSection
        self.design_dict['Material'] = self.material
        self.design_pref_inputs={}
        self.design_pref()
        self.input_dock_inputs = self.input_values()
        self.designPrefDialog = DesignPreferences(input_dictionary=self.input_dock_inputs)


    def set_factored_loads(self, sherd_loads: int, axial_force: int):

        self.shear_loads = sherd_loads
        self.axial_force = axial_force
        self.design_dict['Load.Shear'] = self.shear_loads
        self.design_dict['Load.Axial'] = self.axial_force

    def set_bolt(self, bolt_type: str, bolt_diameter="All", bolt_grade = "All"):
        self.bolt_type = bolt_type
        self.bolt_diameter = bolt_diameter
        self.bolt_grade = bolt_grade
        self.design_dict['Bolt.Type'] = self.bolt_type
        self.design_dict['Bolt.Diameter'] = self.bolt_diameter
        self.design_dict['Bolt.Grade'] = self.bolt_grade

    def set_plate(self, plate_thickness='All'):
        self.plate_thickness = plate_thickness
        self.design_dict['Connector.Plate.Thickness_List'] = self.plate_thickness
    def design_pref(self):
        option_list = self.input_values()
        new_list = self.customized_input()
        updated_list = self.input_value_changed()
        out_list = self.output_values(False)
        data = {}
        last_design_folder = os.path.join('../../ResourceFiles', 'last_designs')
        last_design_file = str(self.module_name()).replace(' ', '') + ".osi"
        last_design_file = os.path.join(last_design_folder, last_design_file)
        last_design_dictionary = {}
        if not os.path.isdir(last_design_folder):
            os.mkdir(last_design_folder)
        if os.path.isfile(last_design_file):
            with open(str(last_design_file), 'r') as last_design:
                last_design_dictionary = yaml.safe_load(last_design)
        if isinstance(last_design_dictionary, dict):
            self.setDictToUserInputs(last_design_dictionary, option_list, data, new_list)
            if "out_titles_status" in last_design_dictionary.keys():
                title_status = last_design_dictionary["out_titles_status"]
                print("titles", title_status)
                title_count = 0
                out_titles = []
                title_repeat = 1
                for out_field in out_list:
                    if out_field[2] == TYPE_TITLE:
                        title_name = out_field[1]
                        if title_name in out_titles:
                            title_name += str(title_repeat)
                            title_repeat += 1
                        # self.output_title_fields[title_name][0].setVisible(title_status[title_count])
                        title_count += 1
                        out_titles.append(title_name)
        self.ui_loaded = True

    def design_fn(self, op_list, data_list):
        design_dictionary = {}
        self.input_dock_inputs = {}
        for op in op_list:
            # widget = self.dockWidgetContents.findChild(QtWidgets.QWidget, op[0])
            if op[2] == TYPE_COMBOBOX:
                # des_val = widget.currentText()
                des_val = self.design_dict[op[0]]
                d1 = {op[0]: des_val}
            elif op[2] == TYPE_MODULE:
                des_val = op[0]
                module = op[1]
                d1 = {op[0]: module}
            elif op[2] == TYPE_COMBOBOX_CUSTOMIZED:
                des_val = data_list[op[0]]
                d1 = {op[0]: des_val}
            elif op[2] == TYPE_TEXTBOX:
                des_val = self.design_dict[op[0]]
                d1 = {op[0]: des_val}
            elif op[2] == TYPE_NOTE:
                # widget = self.dockWidgetContents.findChild(QtWidgets.QWidget, op[0] + "_note")
                # des_val = widget.text()
                d1 = {op[0]: self.design_dict[op[0]]}
            else:
                d1 = {}
            design_dictionary.update(d1)
            self.input_dock_inputs.update(d1)

        for design_pref_key in self.design_pref_inputs.keys():
            if design_pref_key not in self.input_dock_inputs.keys():
                self.input_dock_inputs.update({design_pref_key: self.design_pref_inputs[design_pref_key]})
        if self.designPrefDialog.flag:
            print('flag true')

            # des_pref_input_list = self.input_dictionary_design_pref()
            # edit_tabs_list = self.edit_tabs()
            # edit_tabs_remove = list(filter(lambda x: x[2] == TYPE_REMOVE_TAB, edit_tabs_list))
            # remove_tab_name = [x[0] for x in edit_tabs_remove]
            # # remove_tabs = list(filter(lambda x: x[0] in remove_tab_name, des_pref_input_list))
            # #
            # # remove_func_name = edit_tabs_remove[3]
            # result = None
            # for edit in self.edit_tabs():
            #     (tab_name, input_dock_key_name, change_typ, f) = edit
            #     remove_tabs = list(filter(lambda x: x[0] in remove_tab_name, des_pref_input_list))
            #
            #     input_dock_key = self.dockWidgetContents.findChild(QtWidgets.QWidget, input_dock_key_name)
            #     result = list(filter(lambda get_tab:
            #                          self.designPrefDialog.ui.findChild(QtWidgets.QWidget, get_tab[0]).objectName() !=
            #                          f(input_dock_key.currentText()), remove_tabs))
            #
            # if result is not None:
            #     des_pref_input_list_updated = [i for i in des_pref_input_list if i not in result]
            # else:
            #     des_pref_input_list_updated = des_pref_input_list
            #
            # for des_pref in des_pref_input_list_updated:
            #     tab_name = des_pref[0]
            #     input_type = des_pref[1]
            #     input_list = des_pref[2]
            #     tab = self.designPrefDialog.ui.findChild(QtWidgets.QWidget, tab_name)
            #     for key_name in input_list:
            #         key = tab.findChild(QtWidgets.QWidget, key_name)
            #         if key is None:
            #             continue
            #         if input_type == TYPE_TEXTBOX:
            #             val = key.text()
            #             design_dictionary.update({key_name: val})
            #         elif input_type == TYPE_COMBOBOX:
            #             val = key.currentText()
            #             design_dictionary.update({key_name: val})
        else:
            print('flag false')

            for without_des_pref in self.input_dictionary_without_design_pref():
                input_dock_key = without_des_pref[0]
                input_list = without_des_pref[1]
                input_source = without_des_pref[2]
                for key_name in input_list:
                    if input_source == 'Input Dock':
                        design_dictionary.update({key_name: design_dictionary[input_dock_key]})
                    else:
                        val = self.get_values_for_design_pref(self, key_name, design_dictionary)
                        design_dictionary.update({key_name: val})

            for dp_key in self.design_pref_inputs.keys():
                design_dictionary[dp_key] = self.design_pref_inputs[dp_key]

        self.design_inputs = design_dictionary
        self.design_inputs = design_dictionary

    def update_material_db(self, grade, material):

        fy_20 = int(material.fy_20)
        fy_20_40 = int(material.fy_20_40)
        fy_40 = int(material.fy_40)
        fu = int(material.fu)
        elongation = 0

        if fy_20 > 350:
            elongation = 20
        elif 250 < fy_20 <= 350:
            elongation = 22
        elif fy_20 <= 250:
            elongation = 23

        conn = sqlite3.connect(PATH_TO_DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO Material (Grade,[Yield Stress (< 20)],[Yield Stress (20 -40)],
        [Yield Stress (> 40)],[Ultimate Tensile Stress],[Elongation ]) VALUES (?,?,?,?,?,?)''',
                  (grade, fy_20, fy_20_40, fy_40, fu, elongation))
        conn.commit()
        c.close()
        conn.close()

    def setDictToUserInputs(self, uiObj, op_list, data, new):

        self.load_input_error_message = "Invalid Inputs Found! \n"

        for uiObj_key in uiObj.keys():
            if str(uiObj_key) in [KEY_SUPTNGSEC_MATERIAL, KEY_SUPTDSEC_MATERIAL, KEY_SEC_MATERIAL,
                                  KEY_CONNECTOR_MATERIAL,
                                  KEY_BASE_PLATE_MATERIAL]:
                material = uiObj[uiObj_key]
                material_validator = MaterialValidator(material)
                if material_validator.is_already_in_db():
                    pass
                elif material_validator.is_format_custom():
                    if material_validator.is_valid_custom():
                        self.update_material_db(grade=material, material=material_validator)
                        input_dock_material = []
                        input_dock_material.clear()
                        for item in connectdb("Material"):
                            input_dock_material.append(item)
                    else:
                        self.load_input_error_message += \
                            str(uiObj_key) + ": (" + str(material) + ") - Default Value Considered! \n"
                        continue
                else:
                    self.load_input_error_message += \
                        str(uiObj_key) + ": (" + str(material) + ") - Default Value Considered! \n"
                    continue

            if uiObj_key not in [i[0] for i in op_list]:
                self.design_pref_inputs.update({uiObj_key: uiObj[uiObj_key]})

        # for op in op_list:
        #     key_str = op[0]
        #     key = self.dockWidgetContents.findChild(QtWidgets.QWidget, key_str)
        #     if op[2] == TYPE_COMBOBOX:
        #         if key_str in uiObj.keys():
        #             index = key.findText(uiObj[key_str], QtCore.Qt.MatchFixedString)
        #             if index >= 0:
        #                 key.setCurrentIndex(index)
        #             else:
        #                 if key_str in [KEY_SUPTDSEC, KEY_SUPTNGSEC]:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Select from available Sections! \n"
        #                 else:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Default Value Considered! \n"
        #     elif op[2] == TYPE_TEXTBOX:
        #         if key_str in uiObj.keys():
        #             if key_str == KEY_SHEAR or key_str == KEY_AXIAL or key_str == KEY_MOMENT:
        #                 if uiObj[key_str] == "":
        #                     pass
        #                 elif float(uiObj[key_str]) >= 0:
        #                     pass
        #                 else:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Load should be positive integer! \n"
        #                     uiObj[key_str] = ""
        #
        #             key.setText(uiObj[key_str] if uiObj[key_str] != 'Disabled' else "")
        #     elif op[2] == TYPE_COMBOBOX_CUSTOMIZED:
        #         if key_str in uiObj.keys():
        #             for n in new:
        #
        #                 if n[0] == key_str and n[0] == KEY_SECSIZE:
        #                     if set(uiObj[key_str]) != set(n[1]([self.dockWidgetContents.findChild(QtWidgets.QWidget,
        #                                                                                           KEY_SEC_PROFILE).currentText()])):
        #                         key.setCurrentIndex(1)
        #                     else:
        #                         key.setCurrentIndex(0)
        #                     data[key_str + "_customized"] = uiObj[key_str]
        #
        #                 elif n[0] == key_str and n[0] != KEY_SECSIZE:
        #                     if set(uiObj[key_str]) != set(n[1]()):
        #                         key.setCurrentIndex(1)
        #                     else:
        #                         key.setCurrentIndex(1)
        #                     data[key_str + "_customized"] = uiObj[key_str]
        #
        #     else:
        #         pass

        if self.load_input_error_message != "Invalid Inputs Found! \n":
            logging.log(self.load_input_error_message)

    def show_error_msg(self, error):
          # show only first error message.
        logging.error(error,)
    def common_function_for_save_and_design(self, trigger_type):

        # @author: Amir

        option_list = FinPlateConnection.input_values(self)
        new_list = self.customized_input()

        data = {}

        if len(new_list)>0:
            for i in new_list:
                data_key = i[0]
                data[data_key] = [all_val for all_val in i[1]()]



        self.design_fn(option_list, data)
        print(data)
        if trigger_type == "Save":
            # self.saveDesign_inputs()
            pass
        elif trigger_type == "Design_Pref":

            if self.prev_inputs != self.input_dock_inputs or self.designPrefDialog.changes != QDialog.Accepted:
                self.designPrefDialog = DesignPreferences(main, self, input_dictionary=self.input_dock_inputs)

                if 'Select Section' in self.input_dock_inputs.values():
                    self.designPrefDialog.flag = False
                else:
                    self.designPrefDialog.flag = True

                # if self.prev_inputs != {}:
                #     self.design_pref_inputs = {}

        else:
            self.design_button_status = True
            for input_field in self.dockWidgetContents.findChildren(QtWidgets.QWidget):
                if type(input_field) == QtWidgets.QLineEdit:
                    input_field.textChanged.connect(self.clear_output_fields)
                elif type(input_field) == QtWidgets.QComboBox:
                    input_field.currentIndexChanged.connect(self.clear_output_fields)
            self.textEdit.clear()
            with open("logging_text.log", 'w') as log_file:
                pass

            error = self.func_for_validation( self.design_inputs)
            status = self.design_status
            print(status)

            if error is not None:
                self.show_error_msg(error)
                return

            out_list = main.output_values(main, status)
            for option in out_list:
                if option[2] == TYPE_TEXTBOX:
                    txt = self.dockWidgetContents_out.findChild(QtWidgets.QWidget, option[0])
                    txt.setText(str(option[3]))
                    if status:
                        txt.setVisible(True if option[3] != "" and txt.isVisible() else False)
                        txt_label = self.dockWidgetContents_out.findChild(QtWidgets.QWidget, option[0]+"_label")
                        txt_label.setVisible(True if option[3] != "" and txt_label.isVisible() else False)

                elif option[2] == TYPE_OUT_BUTTON:
                    self.dockWidgetContents_out.findChild(QtWidgets.QWidget, option[0]).setEnabled(True)

            # self.progress_bar.setValue(50)
            self.output_title_change(main)

            last_design_folder = os.path.join('../../ResourceFiles', 'last_designs')
            if not os.path.isdir(last_design_folder):
                os.mkdir(last_design_folder)
            last_design_file = str(main.module_name(main)).replace(' ', '') + ".osi"
            last_design_file = os.path.join(last_design_folder, last_design_file)
            out_titles_status = []
            out_titles = []
            title_repeat = 1
            for option in out_list:
                if option[2] == TYPE_TITLE:
                    title_name = option[1]
                    if title_name in out_titles:
                        title_name += str(title_repeat)
                        title_repeat += 1
                    if self.output_title_fields[title_name][0].isVisible():
                        out_titles_status.append(1)
                    else:
                        out_titles_status.append(0)
                    out_titles.append(title_name)
            self.design_inputs.update({"out_titles_status": out_titles_status})
            with open(str(last_design_file), 'w') as last_design:
                yaml.dump(self.design_inputs, last_design)
            self.design_inputs.pop("out_titles_status")
            # self.progress_bar.setValue(60)

            # if status is True and main.module in [KEY_DISP_FINPLATE, KEY_DISP_BEAMCOVERPLATE,
            #                                       KEY_DISP_BEAMCOVERPLATEWELD, KEY_DISP_CLEATANGLE,
            #                                       KEY_DISP_ENDPLATE, KEY_DISP_BASE_PLATE, KEY_DISP_SEATED_ANGLE,
            #                                       KEY_DISP_TENSION_BOLTED, KEY_DISP_TENSION_WELDED,KEY_DISP_COLUMNCOVERPLATE,
            #                                       KEY_DISP_COLUMNCOVERPLATEWELD, KEY_DISP_COLUMNENDPLATE]:

            # ##############trial##############
            # status = True
            # ##############trial##############
            if status is True and main.module in [KEY_DISP_FINPLATE, KEY_DISP_BEAMCOVERPLATE,
                                                  KEY_DISP_BEAMCOVERPLATEWELD, KEY_DISP_CLEATANGLE,
                                                  KEY_DISP_ENDPLATE, KEY_DISP_BASE_PLATE, KEY_DISP_SEATED_ANGLE,
                                                  KEY_DISP_TENSION_BOLTED, KEY_DISP_TENSION_WELDED,
                                                  KEY_DISP_COLUMNCOVERPLATE,
                                                  KEY_DISP_COLUMNCOVERPLATEWELD, KEY_DISP_COLUMNENDPLATE, KEY_DISP_BCENDPLATE, KEY_DISP_BB_EP_SPLICE]:
                # print(self.display, self.folder, main.module, main.mainmodule)
                print("common start")
                self.commLogicObj = CommonDesignLogic(self.display, self.folder, main.module, main.mainmodule)
                print("common start")
                status = main.design_status
                ##############trial##############
                # status = True
                ##############trial##############

                module_class = self.return_class(main.module)
                # self.progress_bar.setValue(80)
                print("3D start")
                self.commLogicObj.call_3DModel(status, module_class)
                print("3D end")
                self.display_x = 90
                self.display_y = 90
                for chkbox in main.get_3d_components(main):
                    self.frame.findChild(QtWidgets.QCheckBox, chkbox[0]).setEnabled(True)
                for action in self.menugraphics_component_list:
                    action.setEnabled(True)
                fName = str('./ResourceFiles/images/3d.png')
                file_extension = fName.split(".")[-1]

                # if file_extension == 'png':
                #     self.display.ExportToImage(fName)
                #     im = Image.open('./ResourceFiles/images/3d.png')
                #     w,h=im.size
                #     if(w< 640 or h < 360):
                #         print('Re-taking Screenshot')
                #         self.resize(700,500)
                #         self.outputDock.hide()
                #         self.inputDock.hide()
                #         self.textEdit.hide()
                #         QTimer.singleShot(0, lambda:self.retakeScreenshot(fName))

            else:
                for fName in ['3d.png', 'top.png',
                              'front.png', 'side.png']:
                    with open("./ResourceFiles/images/"+fName, 'w'):
                        pass
                self.display.EraseAll()
                for chkbox in main.get_3d_components(main):
                    self.frame.findChild(QtWidgets.QCheckBox, chkbox[0]).setEnabled(False)
                for action in self.menugraphics_component_list:
                    action.setEnabled(False)

            # self.progress_bar.setValue(100)




fin = FinPlate(CONN_CFBW,'HB 150','JB 150', 'E 165 (Fe 290)')
fin.set_factored_loads(2,3)
fin.set_bolt(TYP_FRICTION_GRIP)
fin.set_plate()
fin.common_function_for_save_and_design('Design')
