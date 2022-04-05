from gui import actions
import tkinter as tk

"""
Window configuration methods
"""
def configure_window(gui_app, width, height):
    # Set basic window parameters
    gui_app.title("Landis")
    gui_app.resizable(False, False)
    gui_app.geometry(f"{width}x{height}") # Set size
    gui_app.attributes('-topmost',True)

    # Configure layout
    width = {"classifier": 225, "status": 300, "settings": 150}
    gui_app.columnconfigure(0, minsize=width["classifier"])
    gui_app.columnconfigure(1, minsize=width["status"])
    gui_app.columnconfigure(2, minsize=width["settings"])
    gui_app.rowconfigure(0, minsize=80)

def configure_frames(gui_app, windowwidth, windowheight):
    # Frame positioning
    gui_app.frm_logger.grid    (row=0, column=0, columnspan=3 )
    gui_app.frm_classifier.grid(row=1, column=0, sticky="nsew")
    gui_app.frm_status.grid    (row=1, column=1, sticky="nsew")
    gui_app.frm_settings.grid  (row=1, column=2, sticky="nsew")
    gui_app.heatmap_canvas.grid(row=2, column=0, columnspan=3 )

    # Initially draw empty heatmap images
    gui_app.heatmap_canvas.create_image(0, 10, anchor=tk.NW, image=gui_app.kb_image)
    gui_app.heatmap_canvas.create_image(580, 25, anchor=tk.NW, image=gui_app.ms_image)

    # Configure frame grids
    gui_app.frm_classifier.columnconfigure(0, minsize=30)
    gui_app.frm_status.columnconfigure(0, minsize=75)
    gui_app.frm_status.columnconfigure(4, minsize=50)
    gui_app.frm_settings.columnconfigure(2, minsize=30)
    gui_app.frm_settings.rowconfigure(1, minsize=15)
    gui_app.frm_settings.rowconfigure(4, minsize=15)

def configure_logger_widgets(gui_app):
    gui_app.lbl_running.grid  (row=0, column=0, columnspan=2)
    gui_app.lbl_loglength.grid(row=1, column=0, sticky="e")
    gui_app.lbl_time.grid     (row=1, column=1, sticky="w")
    # Fill text fields with initial values
    actions.update_lbl_status("Not started")

def configure_classifier_widgets(gui_app):
    # Adjust widgets
    gui_app.btn_profile.config(width=8)
    gui_app.btn_method.config (width=8)
    gui_app.btn_target.config (width=8)

    # Position widgets in frame
    gui_app.lbl_method.grid(row=0, column=1)
    gui_app.btn_method.grid(row=0, column=2)
    gui_app.lbl_target.grid(row=1, column=1)
    gui_app.btn_target.grid(row=1, column=2)
    gui_app.btn_verify.grid(row=2, column=2)

def configure_status_widgets(gui_app):
    # Logger control
    gui_app.btn_toggle.grid(row=0, column=1, padx=5)
    gui_app.btn_stop.grid  (row=0, column=2, padx=5)
    gui_app.btn_save.grid  (row=0, column=3, padx=5)
    # Prediction results
    gui_app.lbl_results.grid  (row=1, column=0, pady=10)
    gui_app.lbl_pred.grid     (row=1, column=0, columnspan=5)
    gui_app.lbl_pred_conf1.grid(row=3, column=0, columnspan=5)
    gui_app.lbl_pred_conf2.grid(row=4, column=0, columnspan=5)
    gui_app.lbl_pred_conf3.grid(row=5, column=0, columnspan=5)
    gui_app.lbl_pred_conf4.grid(row=6, column=0, columnspan=5)
    gui_app.lbl_pred_conf5.grid(row=7, column=0, columnspan=5)
    gui_app.lbl_pred_conf6.grid(row=8, column=0, columnspan=5)
    gui_app.lbl_pred_conf7.grid(row=9, column=0, columnspan=5)

def configure_settings_widgets(gui_app):
    gui_app.lbl_profile.grid(row=0, column=0, sticky="e", padx=5)
    gui_app.btn_profile.grid(row=0, column=1, sticky="w", padx=5)

    # Position pausekey widgets
    gui_app.lbl_pausekey.grid(row=2, column=0, columnspan=2)
    gui_app.ent_pausekey.grid(row=3, column=0, sticky="e", padx=5)
    gui_app.btn_setpausekey.grid(row=3, column=1, sticky="w", padx=5)

    # Enter logfile directory
    gui_app.lbl_log_dir.grid(row=5, column=0, columnspan=2, pady=5)
    gui_app.ent_log_dir.grid(row=6, column=0, columnspan=2)
    gui_app.btn_set_log_dir.grid(row=7, column=0, columnspan=2)
    gui_app.chk_override.grid(row=8, column=0, columnspan=2, pady=5)

    # Info bar (along the bottom, hidden initially)
    gui_app.lbl_settings_info.grid(row=9, column=0, columnspan=3, sticky="w")

    # Fill text fields with initial values
    actions.update_lbl_pausekey(gui_app.pausekey)
    actions.update_lbl_logdir()
