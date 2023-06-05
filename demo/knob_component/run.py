import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        gr.Knob(label="Attack", info="Set attack")
        gr.Knob(label="Decay", info="Set decay")
        gr.Knob(label="Sustain", info="Set sustain")
        gr.Knob(label="Release", info="Set release")

demo.launch()
