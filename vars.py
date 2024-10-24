from os import getcwd

main_path = getcwd()

program_name = "BanAdder"
program_version = "1.1"

program_ui = f"{main_path}/{program_name} {program_version}/Program/banadder.ui"
program_icons = f"{main_path}/{program_name} {program_version}/Program/Icons/"
program_presets = f"{main_path}/{program_name} {program_version}/Presets/"

rp_key = "-rp"

pattern_redactor_style_default = "background-color: rgb(140, 140, 140);" \
                                 "border-radius: 5px;" \
                                 "border: 3px solid rgb(74, 74, 74);"

pattern_redactor_style_chosen = "background-color: rgb(140, 140, 140); " \
                                "border-radius: 5px; " \
                                "border: 4px solid orange;"

unicode_convertor_ignore = "QWERTYUIOPASDFGHJKLZXCVBNM" \
                           "qwertyuiopasdfghjklzxcvbnm" \
                           "1234567890 " \
                           "'№;%:?+-=@#$%^&*()_\\|/`~,.!\""
