import cv2

class DrawLineWidget(object):
    def __init__(self):
        self.coordinates_list = []
        self.original_image = cv2.imread('messi.jpg')
        self.clone = self.original_image.copy()

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

        # List to store start/end points
        self.image_coordinates = []

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            print('Starting: {}, Ending: {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
            print(self.coordinates_list)
            if len(self.coordinates_list) == 3:
                print("Finished")
            # Draw line
            if (len(self.coordinates_list) < 1):
                cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
                self.coordinates_list.append((self.image_coordinates[0], self.image_coordinates[1]))

            cv2.imshow("image", self.clone) 

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone

if __name__ == '__main__':
    draw_line_widget = DrawLineWidget()
    while len(draw_line_widget.coordinates_list) < 3:
        cv2.imshow('image', draw_line_widget.show_image())
        key = cv2.waitKey(1)
        cv2.imshow('image', draw_line_widget.show_image())


        # Close program with keyboard 'q'
        if key == ord('q'):
            cv2.destroyAllWindows()
            exit(1)