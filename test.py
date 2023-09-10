from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image as CoreImage
from kivy.uix.button import Button

# Preload and cache images
image_cache = {
    'image1': CoreImage('image1.png'),
    'image2': CoreImage('image2.png'),
}

class BasicImageButton(ButtonBehavior, Image):
    def __init__(self, source_key, **kwargs):
        super(BasicImageButton, self).__init__(**kwargs)
        self.source_key = source_key  # Use a key to specify the image source

    def update_image(self):
        # Update the button's image using the cached CoreImage
        core_img = image_cache.get(self.source_key)
        if core_img:
            self.texture = core_img.texture

class BasicImageButtonApp(App):
    def build(self):
        # Create a layout
        layout = BoxLayout(orientation='vertical')

        # Create BasicImageButtons with specified image keys
        button1 = BasicImageButton(source_key='image1')
        button2 = BasicImageButton(source_key='image2')

        button1.size_hint = (None, None)
        button2.size_hint = (None, None)

        button1.width = button2.width = 200
        button1.height = button2.height = 200

        # Bind functions to change images on button press
        button1.bind(on_press=lambda instance: instance.update_image())
        button2.bind(on_press=lambda instance: instance.update_image())

        # Create a button to reset images
        reset_button = Button(text="Reset Images")
        reset_button.size_hint = (None, None)
        reset_button.width = 200
        reset_button.height = 50
        reset_button.bind(on_press=self.reset_images)

        # Add the buttons to the layout
        layout.add_widget(button1)
        layout.add_widget(button2)
        layout.add_widget(reset_button)

        return layout

    def reset_images(self, instance):
        print("Reset Images button pressed")  # Check if the button press event is triggered
        # Reset the images to their initial state
        for key in image_cache:
            print(f"Reloading image: {key}.png")  # Check if images are being reloaded
            image_cache[key] =  CoreImage('image2.png')

if __name__ == '__main__':
    BasicImageButtonApp().run()