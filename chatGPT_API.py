import requests
import base64
import os
import sys
import webbrowser
import replicate
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from image_process import overlay_image_rgb
from image_process import save_image as save_img
import cv2


replicate = replicate.Client(api_token='--')

class ChatGpt:
    def __init__(self, file_name):
        self.file_path = file_name
        self.header = {
            "Content-Type": "application/json",
            "Authorization": "--"
        }
        self.last_response = None

    def encode_image(self):
        with open(self.file_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_prompt(self, prompt, image_encoded=None):
        if image_encoded:
            return {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_encoded}"}}
                        ]
                    }
                ],
                "max_tokens": 100
            }
        else:
            return {
                "model": "gpt-4-1106-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ],
                "max_tokens": 400
            }

    def class_response(self):
        fixed_prompt = "Please describe the key features of the object in this line drawing in one sentence, as a pareidolia. It can be any category of specific objects. You have to be creative as possible as you can. DO NOT answer with words similar to 'abstract', 'whimsical', 'geometry', 'kinetic', 'polygon', 'origami'. Although the shape is vague, you must provide an answer nonetheless. Answer should be one sentence in the form of one noun and a phrase that modifies it. Rather than starting with 'it looks like,' start with 'It is"
        image_encoded = self.encode_image()
        self.payload = self.generate_prompt(fixed_prompt, image_encoded)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.header, json=self.payload)
        response_json = response.json()
        description = response_json['choices'][0]['message']['content'] 
        print(description)

        self.payload = self.generate_prompt(description+"=> Reduce this sentence to just 1-2 words. Just answer the words.")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.header, json=self.payload)
        response_json = response.json() 
        self.last_response = response_json['choices'][0]['message']['content'] 

        return [description, self.last_response]

    def story_generator(self):
        if self.last_response is None:
            raise ValueError("No response available to generate story. Run class_response first.")

        fixed_prompt = f"Write a mythological story about how {self.last_response} became a constellation. The story should be about 200 words"
        self.payload = self.generate_prompt(fixed_prompt)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.header, json=self.payload)
        response_json = response.json()
        story = response_json['choices'][0]['message']['content']
        #self.payload = self.generate_prompt(f"what is the title of this story below. Do not add any other text but just tell me the name of the constellation. \n {self.last_response}")
        #response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.header, json=self.payload)
        #response_json = response.json()
        #title = response_json['choices'][0]['message']['content']
        
        return story

    def generate_image(self, description):
        output = replicate.run(
            "cyber42/remedios_varo:c8acb09ba51d3c1f0d87c7a69266ca4d1550761ee01a9b102ccd22df723ef5fd",
            input={
                "image": open(self.file_path, 'rb'),
                "width": 640,
                "height": 480,
                "prompt": f"In the style of Remedios Varo, {description}, white background, grayscale",
                "refine": "expert_ensemble_refiner",
                "scheduler": "DDIM",
                "lora_scale": 0.6,
                "num_outputs": 3,
                "guidance_scale": 10,
                "apply_watermark": False,
                "high_noise_frac": 0.78,
                "negative_prompt": "\"broken, disfigured, dismembered people, low quality, incomplete\"",
                "prompt_strength": 0.78,
                "num_inference_steps": 150
            }
        )
        return output

    def choose_image(self, image_urls, overlay_image):
        if not image_urls:
            raise ValueError("No image URLs provided")

        self.selected_image = None

        def select_image(url):
            self.selected_image = url
            root.destroy()

        root = tk.Tk()
        root.title("Select an Image")
        frame = tk.Frame(root)
        frame.pack()

        for url in image_urls:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img.save(f"./generations/{timestamp}.png")

            img = img.resize((640, 480), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            button = tk.Button(frame, image=img_tk, command=lambda u=url: select_image(u))
            button.image = img_tk
            button.pack(side=tk.LEFT)

        root.mainloop()

        if self.selected_image:
            response = requests.get(self.selected_image)
            selected_img = Image.open(BytesIO(response.content)).convert("RGBA")
            #x, y = selected_img.size

            #sky_img = Image.open(overlay_image).convert("RGBA").resize((x,y))

            #selected_img.putalpha(180)
            #sky_img.putalpha(180)

            #final_img = Image.alpha_composite(selected_img, sky_img)
            
            line = cv2.cvtColor(np.array(selected_img), cv2.COLOR_RGB2BGR)
            final_img = overlay_image_rgb(cv2.imread(overlay_image), line)

            return final_img
        else:
            raise ValueError("No image selected")
        


def get_next_file_number(folder_path):
    """ Returns the next file number to be used based on the number of files in the folder. """
    num_files = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
    return (num_files // 3) + 1

def save_text_file(content, file_name, folder_path):
    """ Saves content to a text file in the specified folder. """
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def save_image(image, file_name, folder_path):
    """ Saves an image to a file in the specified folder. """
    file_path = os.path.join(folder_path, file_name)
    image.save(file_path)

if __name__ == "__main__":

    file_number = get_next_file_number('output')

    file_name = sys.argv[1]
    chatgpt_instance = ChatGpt(file_name)
    print("Getting class response...")
    description, class_response = chatgpt_instance.class_response()
    print("* Response:", class_response)

    print("Generating story...")
    story = chatgpt_instance.story_generator()
    print("* Story Loaded")

    print("Generating images...")
    image_urls = chatgpt_instance.generate_image(' '.join(description.split()[2:]))

    print("* Click and choose an image.")
    chosen_image = chatgpt_instance.choose_image(image_urls, sys.argv[2])

    output_folder = "./output"
    # Save the title and story
    save_text_file(class_response, f"title_{file_number}.txt", output_folder)
    save_text_file(story, f"story_{file_number}.txt", output_folder)

    # Assuming 'chosen_image' is a PIL image or similar
    #save_image(chosen_image, f"image_{file_number}.png", output_folder)
    save_img(chosen_image, f"{output_folder}/image_{file_number}.png")  


    import os
    print("Check the link http://127.0.0.1:3000/"+os.getcwd().replace("C:","c:")+"/index.html")