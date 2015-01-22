class Todo:
  
  def __init__(self, text):
    self.text = text
    self.done = False

  def to_json_dict(self):
    return {"text" : self.text,
            "done" : self.done}
            
