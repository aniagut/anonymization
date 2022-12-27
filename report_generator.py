from fpdf import FPDF

PLOT_DIR = 'plots'

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297

    def header(self):
        # Custom logo and positioning
        # Create an `assets` folder and put any wide and short image inside
        # Name the image `logo.png`
        self.set_font('Arial', 'B', 14)
        self.cell(0)
        self.cell(5, 1, 'Emotions and gaze analysis report for file dc9fde7e-faab-4236-a470-cb137621eb2a', 0, 0, 'R')
        self.ln(20)

    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, images):
        # Determine how many plots there are per page and set positions
        # and margins accordingly
        if len(images) == 3:
            self.image(images[0], 45, 25, 100, 75)
            self.image(images[1], 45, 105, 100, 75)
            self.image(images[2], 45, 185, 100, 75)
        elif len(images) == 2:
            self.image(images[0], 15, 25, self.WIDTH - 30, self.HEIGHT - 20)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30, self.HEIGHT - 20)
        else:
            self.image(images[0], 45, 25, 100, 75)

    def print_page(self, images):
        # Generates the report
        self.add_page()
        self.page_body(images)

import matplotlib.pyplot as plt
def prepare_first_plot(emotions, timestamps, id):
    plt.plot(timestamps, emotions)
    plt.title(f'Emotions in time for person {id}')
    plt.xlabel('Timestamps [ms]')
    plt.ylabel('Emotions')
    plt.savefig(f'processing/plots/1/{id}.jpg')
    plt.clf()

def prepare_second_plot(emotions_list, count, id):
    plt.pie(count, labels=emotions_list, autopct='%1.1f%%')
    plt.title(f"Percentage distribution of emotions for person {id}")
    plt.savefig(f'processing/plots/2/{id}.jpg')
    plt.clf()

def prepare_third_plot(gaze, timestamps, id):
    plt.plot(timestamps, gaze)
    plt.title(f'Gaze tracking in time for person {id}')
    plt.xlabel('Timestamps [ms]')
    plt.ylabel('Gaze')
    plt.savefig(f'processing/plots/3/{id}.jpg')
    plt.clf()

def prepare_fourth_plot(gaze_list, count, id):
    plt.pie(count, labels=gaze_list, autopct='%1.1f%%')
    plt.title(f"Percentage distribution of gaze for person {id}")

    plt.savefig(f'processing/plots/4/{id}.jpg')
    plt.clf()

def prepare_data_for_plots(input_list):
    plots_files = []
    for person_id, out_list in input_list.items():
        timestamps = []
        emotions = []
        horizontal_gaze = []
        vertical_gaze = []
        for emotion, horizontal, vertical, timestamp in out_list:
            emotions.append(emotion)
            timestamps.append(timestamp)
            if horizontal == 'L':
                horizontal_gaze.append('left')
            elif horizontal == 'C':
                horizontal_gaze.append('center')
            else:
                horizontal_gaze.append('right')
            if vertical == 'U':
                vertical_gaze.append('up')
            elif vertical == 'C':
                vertical_gaze.append('center')
            else:
                vertical_gaze.append('down')

        prepare_first_plot(emotions, timestamps, person_id)
        distinct_emotions = list(set(emotions))
        emotions_count = []
        for distinct_emotion in distinct_emotions:
            emotions_count.append(emotions.count(distinct_emotion))
        prepare_second_plot(distinct_emotions, emotions_count, person_id)
        overall_gaze = []

        for hor, vert in zip(horizontal_gaze, vertical_gaze):
            overall_gaze.append(f"{vert}-{hor}")
        prepare_third_plot(overall_gaze, timestamps, person_id)
        distinct_gazes = list(set(overall_gaze))
        gaze_count = []
        for distinct_gaze in distinct_gazes:
            gaze_count.append(overall_gaze.count(distinct_gaze))
        prepare_fourth_plot(distinct_gazes, gaze_count, person_id)
        for folder_no in range(1,5):
            plots_files.append(f"processing/plots/{folder_no}/{person_id}.jpg")
    return plots_files