From the coding test description, the **UI side** needs to cover a few concrete things — nothing too fancy, but enough to make the demo clean, responsive, and usable.

Here’s the breakdown based strictly on the test’s requirements (and a couple of extras that will help you score well):

---

## **UI Functionalities Required by the Test**

### **1. Input Field to Add RTSP Stream URLs**

* **Text input** where the user can paste an RTSP URL.
* **Add button** to submit the stream.
* Optional: label field so users can name the stream (e.g., “Front Door”).
* Should handle invalid/missing URL gracefully (show a warning).

---

### **2. Display Area for the Live Stream(s)**

* A **video or canvas element** for each added stream.
* Shows the live feed once it connects.
* If disconnected or error → show an error overlay/message.

---

### **3. Option to View Multiple Streams Simultaneously in a Grid Layout**

* Responsive **grid layout**:

  * 1 stream → 1 column
  * 2 streams → 2 columns
  * 3–4 streams → 2x2
  * More → auto-wrap
* Auto-resize video tiles while maintaining aspect ratio.

---

### **4. Basic Stream Controls (Play/Pause)**

* **Play button** → starts/reconnects the WebSocket stream.
* **Pause button** → stops the stream (and FFmpeg process server-side).
* Per-stream control (not global) so user can pause one without affecting others.

---

### **5. Error Handling in the UI**

* Show **status indicators**: “Connecting…”, “Playing”, “Error: Cannot connect”.
* Allow retry/reconnect button.
* Optional toast/alert for user feedback.

---

### **6. Clean, Responsive Design**

* Works well on both desktop and mobile (since they said “responsive”).
* Scales video elements without distorting.
* Controls/buttons are touch-friendly.

---

## **Nice-to-Haves (Score Boosters)**

These are not explicitly required but will improve UX and impression:

* **Remove stream** button (so grid isn’t permanent clutter).
* **Persistent stream list** in localStorage so a page refresh doesn’t wipe it.
* Show **loading spinner** in the tile until the first frame appears.
* **Thumbnail preview** (optional, FFmpeg snapshot) when paused.
* **Mute audio** toggle if you choose to stream audio.

---

If you stick strictly to the **required** parts, you need only:

1. Add RTSP URL → button to start stream.
2. Show streams in a responsive grid.
3. Play/Pause controls per stream.
4. Error messages + retry.

---

If you want, I can mock up a **minimal React UI wireframe** showing exactly where these features sit so you can build it without overengineering. That will keep you in MVP territory while still covering the test’s UX expectations.
