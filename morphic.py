'''

    morphic.py

    a lively GUI for Python
    inspired by Squeak

    written by Jens Mönig
    jens@moenig.org

    translated to Python by WarpedWartWars

    Copyright (C) 2010-2021 by Jens Mönig and WarpedWartWars

    Morphic is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General
    Public License along with this program.  If not, see
    <http://www.gnu.org/licenses/>.


    documentation contents
    ----------------------
    I. inheritance hierarchy
    II. object definition toc
    III. yet to implement
    IV. open issues
    V. browser compatibility
    VI. the big picture
    VII. programming guide
        (1) setting up a web page
            (a) single world
            (b) multiple worlds
            (c) an application
        (2) manipulating morphs
        (3) events
            (a) mouse events
            (b) context menu
            (c) dragging
            (d) dropping
            (e) keyboard events
            (f) resize event
            (g) combined mouse-keyboard events
            (h) text editing events
        (4) stepping
        (5) creating new kinds of morphs
            (a) drawing the shape
            (b) determining extent and arranging submorphs
            (c) pixel-perfect pointing events
            (d) caching the shape
            (e) holes
            (f) updating
            (g) duplicating
        (6) development and user modes
        (7) turtle graphics
        (8) animations
        (9) minifying morphic.py
    VIII. acknowledgements
    IX. contributors


    I. hierarchy
    -------------
    the following tree lists all constructors hierarchically,
    indentation indicating inheritance. Refer to this list to get a
    contextual overview:

    Animation
    Color
    Node
        Morph
            BlinkerMorph
                CursorMorph
            BouncerMorph*
            BoxMorph
                InspectorMorph
                MenuMorph
                MouseSensorMorph*
                SpeechBubbleMorph
            CircleBoxMorph
                SliderButtonMorph
                SliderMorph
            ColorPaletteMorph
                GrayPaletteMorph
            ColorPickerMorph
            DialMorph
            FrameMorph
                ScrollFrameMorph
                    ListMorph
                StringFieldMorph
                WorldMorph
            HandleMorph
            HandMorph
            PenMorph
            ShadowMorph
            StringMorph
            TextMorph
            TriggerMorph
                MenuItemMorph
    Point
    Rectangle


    II. toc
    -------
    the following list shows the order in which all constructors are
    defined. Use this list to locate code in this document:

    Global settings
    Global functions

    Animation
    Color
    Point
    Rectangle
    Node
    Morph
    ShadowMorph
    HandleMorph
    PenMorph
    ColorPaletteMorph
    GrayPaletteMorph
    ColorPickerMorph
    BlinkerMorph
    CursorMorph
    BoxMorph
    SpeechBubbleMorph
    DialMorph
    CircleBoxMorph
    SliderButtonMorph
    SliderMorph
    MouseSensorMorph*
    InspectorMorph
    MenuMorph
    StringMorph
    TextMorph
    TriggerMorph
    MenuItemMorph
    FrameMorph
    ScrollFrameMorph
    ListMorph
    StringFieldMorph
    BouncerMorph*
    HandMorph
    WorldMorph

    * included only for demo purposes


    III. yet to implement
    ---------------------
    - keyboard support for scroll frames and lists
    - virtual keyboard support for Android


    IV. open issues
    ----------------
    - clipboard support (copy & paste) for non-textual data


    V. browser compatibility
    ------------------------
    I have taken great care and considerable effort to make morphic.py
    runnable and appearing exactly the same on all current browsers
    available to me:

    - Firefox for Windows
    - Firefox for Mac
    - Firefox for Android
    - Chrome for Windows
    - Chrome for Mac
    - Chrome for Android
    - Safari for Windows (deprecated)
    - safari for Mac
    - Safari for iOS (mobile)
    - IE for Windows (partial support)
    - Edge for Windows
    - Opera for Windows
    - Opera for Mac


    VI. the big picture
    -------------------
    Morphic.py is completely based on Tkinter and Python, it is
    just Morphic, nothing else. Morphic.py is very basic and covers
    only the bare essentials:

        * a stepping mechanism (a time-sharing multiplexer for 
          lively user interaction ontop of a single OS/browser
          thread)
        * progressive display updates (only dirty rectangles are
          redrawn at each display cycle)
        * a tree structure
        * a single World per Canvas
        * a single Hand per World (but you can support multi-touch
          events)
        * a single text entry focus per World

    In its current state morphic.py doesn't support transforms (you
    cannot rotate Morphs), but with PenMorph there already is a
    simple LOGO-like turtle that you can use to draw onto any
    Morph it is attached to. I'm planning to add special Morphs
    that support these operations later on, but not for every
    Morph in the system. Therefore these additions ("sprites" etc.)
    are likely to be part of other libraries in separate files.

    The purpose of morphic.py is to provide a malleable framework
    that will let me experiment with lively GUIs for my hobby
    horse, which is drag-and-drop, blocks based programming
    languages. Those things will be written using morphic.py as a
    library.


    VII. programming guide
    ----------------------
    Morphic.py provides a library for lively GUIs inside single
    HTML Canvas elements. Each such canvas element functions as a
    "world" in which other visible shapes ("morphs") can be
    positioned and manipulated, often directly and interactively
    by the user. Morphs are tree nodes and may contain any number
    of submorphs ("children").

    All things visible in a morphic World are morphs themselves,
    i.e. all text rendering, blinking cursors, entry fields, menus,
    buttons, sliders, windows and dialog boxes etc. are created
    with morphic.py rather than using HTML DOM elements, and as a
    consequence can be changed and adjusted by the programmer
    regardless of proprietary browser behavior.

    Each World has an invisible "Hand" following the mouse cursor
    (or the user's finger on touch screens) which handles mouse
    events, and may also have keyboard focus to handle key events.

    The basic idea of Morphic is to continuously run display
    cycles and to incrementally update the screen by only
    redrawing those World regions which have been "dirtied" since
    the last redraw. Before each shape is processed for redisplay
    it gets the chance to perform a "step" procedure, thus
    allowing for an illusion of concurrency.


    (1) setting up Morphic
    -------------------------
    Setting up Morphic always involves three steps:
    * making a Tkinter Canvas element,
    * defining a world, and
    * initializing and starting the main loop.


    (a) single world
    -----------------
    Most commonly you will want just one World. This default
    situation is easiest and most straightforward.

    example Python file:

        import morphic
        from tkinter import Frame, Tk

        class MorphicWindow(Frame):
            def __init__(self, master=None):
                Frame.__init__(self, master)
                self.pack()
                self.world = morphic.WorldMorph()
                self.world.isDevMode = True
                self.world.pack()
            def loop(self):
                self.world.loop()
        root = Tk()
        morphic_world = MorphicWindow(master=root)
        morphic_world.loop()

    (c) an application
    -------------------
    Of course, most of the time you don't want to just plain use the
    standard Morphic World "as is" out of the box, but write your own
    application (something like Snap!) in it. For such an application you'll
    create your own morph prototypes, perhaps assemble your own "window
    frame" and bring it all to life in a customized World state. the
    following example creates a simple snake-like mouse drawing game.

    example Python file:

        import morphic
        from tkinter import Frame, Tk

        class MorphicWindow(Frame):
            def __init__(self, master=None):
                Frame.__init__(self, master)
                self.pack()
                self.world = morphic.WorldMorph()
                self.world.isDevMode = False
                self.world.setColor(morphic.Color())
                self.world.pack()

                self.w_ = 100
                self.h_ = 100

                self.x_ = 0
                self.y_ = 0

                while (y * h) < world.height:
                    while (x * w) < world.width:
                        sensor = morphic.MouseSensorMorph()
                        sensor.setPosition(morphic.Point(x * w, y * h))
                        sensor.alpha = 0
                        sensor.setExtent(morphic.Point(w, h))
                        world.add(sensor)
                        x += 1
                    x = 0
                    y += 1
            def loop(self):
                self.world.loop()

        root = Tk()
        morphic_world = MorphicWindow(master=root)
        morphic_world.loop()

    To get an idea how you can craft your own custom morph prototypes I've
    included two examples which should give you an idea how to add
    properties, override inherited methods and use the stepping mechanism
    for "livelyness":

        BouncerMorph
        MouseSensorMorph

    For the sake of sharing a single file I've included those examples in
    morphic.py itself. Usually you'll define your additions in a separate
    file and keep morphic.py untouched.


    (2) manipulating morphs
    -----------------------
    There are many methods to programmatically manipulate morphs. Among the
    most important and common ones among all morphs are the following nine:

    * hide()                   - hides
    * show()                   - shows

    * setPosition(aPoint)      - sets position
    * setExtent(aPoint)        - sets width and height
    * setColor(aColor)         - sets color

    * add(submorph)            - attaches submorph ontop
    * addBack(submorph)        - attaches submorph underneath

    * fullCopy()               - duplication
    * destroy()                - deletion


    (3) events
    ----------
    All user (and system) interaction is triggered by events, which are
    passed on from the root element - the World - to its submorphs. The
    World contains a list of system events it reacts to in its

        initEventListeners()

    method. Currently there are

        - mouse
        - drop
        - keyboard
        - (window) resize

    events.

    These system events are dispatched within the morphic World by the
    World's Hand and its keyboardFocus (usually the active text cursor).


    (a) mouse events:
    -----------------
    The Hand dispatches the following mouse events to relevant morphs:

        mouseDownLeft
        mouseDownMiddle
        mouseDownRight
        mouseClickLeft
        mouseClickMiddle
        mouseClickRight
        mouseDoubleClickLeft
        mouseDoubleClickMiddle
        mouseDoubleClickRight
        mouseEnter
        mouseLeave
        mouseEnterDraggingLeft
        mouseEnterDraggingMiddle
        mouseEnterDraggingRight
        mouseLeaveDraggingLeft
        mouseLeaveDraggingMiddle
        mouseLeaveDraggingRight
        mouseEnterBounds
        mouseLeaveBounds
        mouseMove
        mouseScroll

    If you wish your morph to react to any such event, simply add a method
    of the same name as the event, e.g:

        class MyMorph(SomeOtherMorph):
            ...
            def mouseMove(self, pos=None):
                if pos is not None:
                    pos = Point(0, 0)
                ...

    Most of these methods have an optional parameter that's passed a Point
    indicating the current position of the Hand inside the World. The

        mouseMove(pos, button)

    event method has an additional optional parameter indicating the
    currently pressed mouse button, which is any of 'left', 'middle', or
    'right'. You can use this to let users interact with 3D environments.

    The

        mouseEnterDraggingLeft(morph)
        mouseEnterDraggingMiddle(morph)
        mouseEnterDraggingRight(morph)
        mouseLeaveDraggingLeft(morph)
        mouseLeaveDraggingMiddle(morph)
        mouseLeaveDraggingRight(morph)
        mouseEnterBounds(morph)
        mouseLeaveBounds(morph)

    event methods have an optional parameter passed the morph currently
    being dragged by the Hand, if any.

    Events may be "bubbled" up a morph's owner chain by calling

        self.escalateEvent(functionName, arg)

    in the event handler method's code.

    Likewise, removing the event handler method will make your morph ignore
    the event in question.


    (b) context menu:
    -----------------
    By default right-clicking (or single-finger tap-and-hold) on a morph
    also invokes its context menu (in addition to firing the mouseClickRight
    event). A morph's context menu can be customized by assigning a
    MenuMorph instance to its

        customContextMenu

    property, or altogether suppressed by overriding its inherited

        contextMenu()

    method.


    (c) dragging:
    -------------
    Dragging a morph is initiated when the left mouse button is pressed,
    held, and the mouse is moved.

    You can control whether a morph is draggable by setting its

        isDraggable

    property either to True or False. If a morph isn't draggable itself it
    will pass the pick-up request up its owner chain. This lets you create
    draggable composite morphs like windows, dialog boxes, sliders, etc.

    Sometimes it is desireable to make "template" shapes which cannot be
    moved themselves, but from which instead duplicates can be peeled off.
    This is especially useful for building blocks in construction kits, e.g.
    the Scratch palette. Morphic lets you control this functionality by
    setting the

        isTemplate

    property flag to True for any morph whose "isDraggable" property is
    False. When dragging such a Morph the hand will instead grab a duplicate
    of the template whose "isDraggable" flag is True and whose "isTemplate"
    flag is False, or in other words: a non-template.

    When creating a copy from a template, the copy's

        reactToTemplateCopy()

    method is invoked, if it is present.

    Dragging is indicated by adding a drop shadow to the morph in hand. If a
    morph follows the hand without displaying a drop shadow it is merely
    being moved about, changing its parent morph, e.g. when "dragging" a
    morph handle to resize its owner, or when "dragging" a slider button.

    Right before a morph is picked up its

        selectForEdit()

    and

        prepareToBeGrabbed(hand)

    methods are invoked, each if it is present. The optional

        selectForEdit()

    method, if implemented, must return the object that is to be picked up.
    In addition to just returning the original object chosen by the user
    your method can also modify the target's environment and instead return
    a copy of the selected morph if, for example, you would like to
    implement a copy-on-write mechanism such as in Snap!.

    Immediately after the pick-up the former parent's

        reactToGrabOf(grabbedMorph)

    method is called, again only if it exists.

    Similar to events, these  methods are optional and don't exist by
    default. For a simple example of how they can be used to adjust scroll
    bars in a scroll frame please have a look at their implementation in
    FrameMorph.


    (d) dropping:
    -------------
    Dropping is triggered when the left mouse button is either pressed or
    released while the Hand is dragging a morph.

    Dropping a morph causes it to become embedded in a new owner morph. You
    can control this embedding behavior by setting the prospective drop
    target's

        acceptsDrops

    property to either True or False, or by overriding its inherited

        wantsDropOf(aMorph)

    method.

    Right before dropping a morph the designated new parent's optional

        selectForEdit()

    method is invoked if it is present. Again, if implemented this method must return the new parent for the morph that is about to be dropped. Again, in addition to just returning the designated drop-target, your method can also modify its environment and instead return a copy of the new parent.

    Right after a morph has been dropped its

        justDropped(hand)

    method is called, and its new parent's

        reactToDropOf(droppedMorph, hand)

    method is invoked, again only if each method exists.

    Similar to events, these  methods are optional and by default are not
    present in morphs by default (watch out for inheritance, though!). For a
    simple example of how they can be used to adjust scroll bars in a scroll
    frame please have a look at their implementation in FrameMorph.

    Drops of image elements from outside the world canvas are dispatched as

        droppedImage(aCanvas, name)
        droppedSVG(anImage, name)

    events to interested Morphs at the mouse pointer. If you want your Morph
    to e.g. import outside images you can add a droppedImage() and/or
    droppedSVG() method to it. The parameter passed to the event handles is
    a new offscreen canvas element representing a copy of the original image
    element which can be directly used, e.g. by assigning it to another
    Morph's cachedImage property. In the case of a dropped SVG it is an
    image element (not a canvas), which has to be rasterized onto a canvas
    before it can be used. The benefit of handling SVGs as image elements is
    that rasterization can be deferred until the destination scale is known,
    taking advantage of SVG's ability for smooth scaling. If instead SVGs
    are to be rasterized right away, you can set the

        MorphicPreferences.rasterizeSVGs

    preference to True. In this case dropped SVGs also trigger the
    droppedImage() event with a canvas containing a rasterized version of
    the SVG.

    The same applies to drops of audio or text files from outside the world
    canvas.

    Those are dispatched as

        droppedAudio(anAudio, name)
        droppedText(aString, name, type)

    events to interested Morphs at the mouse pointer.

    If none of the above content types can be determined, the file contents
    are dispatched as an ArrayBuffer to interested Morphs:

        droppedBinary(anArrayBuffer, name)

    In case multiple files are dropped simulateneously the events

        beginBulkDrop()
        endBulkDrop()

    are dispatched to to Morphs interested in the bulk operation, and the
    endBulkDrop() event is only signalled after the content's last file has
    been asynchronously made available.


    (e) keyboard events
    -------------------
    The World dispatches the following key events to its active keyboard
    focus:

        keypress
        keydown
        keyup

    Currently the only morphs which act as keyboard focus are CursorMorphs -
    the basic text editing widget - and MenuMorphs. If you wish to add
    keyboard support to your morph, you need to add event handling methods
    for

        processKeyPress(event)
        processKeyDown(event)
        processKeyUp(event)

    and activate them by assigning your morph to the World's

        keyboardFocus

    property.

    Note that processKeyUp() is optional and doesn't have to be present if
    your morph doesn't require it.


    (f) resize event
    ----------------
    The Window resize event is handled by the World and allows the World's
    extent to be adjusted so that it always completely fills the tkinter
    Canvas.

    The World dispatches

        reactToWorldResize(newBounds)

    events to all of its children (toplevel only), allowing each to adjust
    to the new World bounds by implementing a corresponding method, the
    passed argument being the World's new dimensions after completing the
    resize. By default, the "reactToWorldResize" Method does not exist.

    Example:

    Add the following method to your Morph to let it automatically fill the
    whole World except for a 10 pixel border:

        class MyMorph:
            ...
            def reactToWorldResize(self, rect):
                self.changed()
                self.bounds = rect.insetBy(10)
                self.rerender()


    (g) combined mouse-keyboard events
    ----------------------------------
    Occasionally you'll want an object to react differently to a mouse click
    or to some other mouse event while the user holds down a key on the
    keyboard. Such "shift-click", "ctrl-click", or "alt-click" events can be
    implemented by querying the World's

        currentKey

    property inside the function that reacts to the mouse event. This
    property stores the keycode of the key that's currently pressed. Once
    the key is released by the user it reverts to None.


    (h) text editing events
    -----------------------
    Much of Morphic's "liveliness" comes out of allowing text elements
    (instances of either single-lined StringMorph or multi-lined TextMorph)
    to be directly manipulated and edited by users. This requires other
    objects which may have an interest in the text element's state to react
    appropriately. Therefore text elements and their manipulators emit a
    stream of events, mostly by "bubbling" them up the text element's owner
    chain. Text elements' parents are notified about the following events:

    Whenever the user presses a key on the keyboard while a text element is
    being edited, first a

        reactToKeystroke(event)

    is escalated up its parent chain, the "event" parameter being the
    original one received by the World.

    Whenever the input changes, by adding or removing one or more characters,
    an additional

        reactToInput(event)

    is escalated up its parent chain, the "event" parameter again being the
    original one received by the World.

    Note that the "reactToKeystroke" event gets triggered before the input
    changes, and thus before the "reactToInput" event fires.

    Once the user has completed the edit, the following events are
    dispatched:

        accept() - enter was pressed on a single-line text element
        cancel() - esc was pressed on any text element

    Note that "accept" only gets triggered by single-line text elements, as
    the enter key is used to insert line breaks in multi-line elements.
    
    Whenever a text edit is terminated by the user (accepted, cancelled or
    otherwise),

        reactToEdit(StringOrTextMorph)

    is triggered.

    If the MorphicPreferences'

        useSliderForInput

    setting is turned on, a slider is popped up underneath the currently
    edited text element letting the user insert numbers in the given slider
    range. Whenever this happens, i.e. whenever the slider is moved or when
    the slider is pressed, a stream of

        reactToSliderEdit(StringOrTextMorph)

    events is dispatched.

    In addition to user-initiated events, text elements also emit change
    notifications to their direct parents whenever their contents changes.
    That way complex Morphs containing text elements get a chance to react
    if something about the embedded text has been modified programmatically.
    These events are:

        layoutChanged() - sent only from instances of TextMorph
        fixLayout()     - sent from instances of TextMorph and StringMorph

    They are different so that Morphs which contain both multi-line and
    single-line text elements can keep them apart.


    (4) stepping
    ------------
    Stepping is what makes Morphic "magical". Two properties control a
    morph's stepping behavior: the fps attribute and the step() method.

    By default the

        step()

    method does nothing. As you can see in the examples of BouncerMorph and
    MouseSensorMorph you can easily override this inherited method to suit
    your needs.

    By default the step() method is called once per display cycle. Depending
    on the number of actively stepping morphs and the complexity of your
    step() methods this can cause quite a strain on your CPU, and also
    result in your application behaving differently on slower computers than
    on fast ones.

    Setting the

        fps

    property to a number lower than the interval for the main loop lets you
    free system resources (albeit at the cost of a less responsive or slower
    behavior for this particular morph).


    (5) creating new kinds of morphs
    --------------------------------
    The real fun begins when you start to create new kinds of morphs with
    customized shapes. Imagine, e.g. jigsaw puzzle pieces or musical notes.

    When you create your own morphs, you'll want to think about how to
    graphically render it, how to determine its size, and whether it needs
    to arrange any other parts ("submorphs"). There are also ways to specify
    its collision detection behavior and define "untouchable" regions
    ("holes").


    (a) drawing the shape
    ---------------------
    For this you have to override the default

        render(canvas)

    method.

    This method draws the morph's shape on a Canvas.

    You can use the following template for a start:

        class MyMorph:
            ...
            def render(self, canvas):
                if self.rect is not None:
                    canvas.delete(self.rect)
                self.rect = canvas.create_rectangle(
                                self.x, self.y,
                                self.width(), self.height(),
                                fill=str(self.color)
                            )

    It renders the morph as a solid rectangle completely filling its area
    with its current color.


    (b) determining extent and arranging submorphs
    ----------------------------------------------
    If your new morph also needs to determine its extent and, e.g. to
    encompass one or more other morphs, or arrange the layout of its
    submorphs, make sure to also override the default

        fixLayout()

    method.

    NOTE: If you need to set the morph's extent inside, in order to avoid
    infinite recursion instead of calling morph.setExtent() - which will
    in turn call morph.fixLayout() again - directly modify the morph's

        bounds

    property. Bounds is a rectangle on which you can also use the same
    size-setters, e.g. by calling:

        self.bounds.setExtent(...)


    (c) pixel-perfect pointing events
    ---------------------------------
    In case your new morph needs to support pixel-perfect collision detection
    with other morphs or pointing devices such as the mouse or a stylus you
    can set the inherited attribute

        isFreeForm = bool

    to "true" (default is "false"). This makes sense the more your morph's
    visual shape diverges from a rectangle. For example, if you create a
    circular filled morph the default setting will register mouse-events
    anywhere within its bounding box, e.g. also in the transparent parts
    between the bounding box's corners outside of the circle's bounds.
    Instead you can specify your irregulary shaped morph to only register
    pointing events (mouse and touch) on solid, non-transparent parts.

    Notice, however, that such pixel-perfect collision detection might
    strain processing resources, especially if applied liberally.

    In order to mitigate unfavorable processor loads for pixel-perfect
    collision deteciton of irregularly shaped morphs there are two strategies
    to consider: Caching the shape and specifying "untouchable" regions.


    (d) caching the shape
    ---------------------
    In case of pixel-perfect free-form collision detection it makes sense to
    cache your morph's current shape, so it doesn't have to be re-drawn onto a
    new Canvas element every time the mouse moves over its bounding box.
    For this you can set then inherited

        isCachingImage = bool

    attribute to "true" instead of the default "false" value. This will
    significantly speed up collision detection and smoothen animations that
    continuously perform collision detection. However, it will also consume
    more memory. Therefore it's best to use this setting with caution.

    Snap! caches the shapes of sprites but not those of blocks. Instead it
    manages the insides of C- and E-shaped blocks through the morphic "holes"
    mechanism.


    (e) holes
    ---------
    An alternative albeit not as precise and general way for handling
    irregularly shaped morphs with "untouchable" regions is to specify a set
    of rectangular areas in which pointing events (mouse or touch) are not
    registered.

    By default the inherited

        holes = []

    property is an empty array. You can add one or more morphic Rectangle
    objects to this list, representing regions, in which occurring events will
    instead be passed on to the morph underneath.

    Note that, same with the render() method, the coordinates of these
    rectangular holes must be specified relative to your morph's position.

    If you specify holes you might find the need to adjust their layout
    depending on the layout of your morph. To accomplish this you can override
    the inherited

        fixHolesLayout()

    method.


    (f) updating
    ------------
    One way for morphs to become alive is form them to literally "morph" their
    shape depending on whicher contest you wish them to react to. For example,
    you might want the user to interactively draw a shape using their fingers
    on a touch screen device, or you want the user to be able to "pinch" or
    otherwise distort a shape interactively. In all of these situations you'll
    want your morph to frequently rerender its shape.

    You can accomplish this, by calling

        rerender()

    after every change to your morph's appearance that requires rerendering.

    Such changes are usually only happening when the morph's dimensions or
    other visual properties - such as its color - changes.


    (g) duplicating
    ---------------
    If your new morph stores or references to other morphs outside of
    the submorph tree in other properties, be sure to also override the
    default

        updateReferences()

    method if you want it to support duplication.


    (6) development and user modes
    ------------------------------
    When working with Squeak on Scratch or BYOB among the features I
    like the best and use the most is inspecting what's going on in
    the World while it is up and running. That's what development mode
    is for (you could also call it debug mode). In essence development
    mode controls which context menu shows up. In user mode right
    clicking (or double finger tapping) a morph invokes its

        customContextMenu

    property, whereas in development mode only the general

        developersMenu()

    method is called and the resulting menu invoked. The developers'
    menu features Gui-Builder-wise functionality to directly inspect,
    take apart, reassamble and otherwise manipulate morphs and their
    contents.

    Instead of using the "customContextMenu" property you can also
    assign a more dynamic contextMenu by overriding the general

        userMenu()

    method with a customized menu constructor. The difference between
    the customContextMenu property and the userMenu() method is that
    the former is also present in development mode and overrides the
    developersMenu() result. For an example of how to use the
    customContextMenu property have a look at TextMorph's evaluation
    menu, which is used for the Inspector's evaluation pane.

    When in development mode you can inspect every Morph's properties
    with the inspector, including all of its methods. The inspector
    also lets you add, remove and rename properties, and even edit
    their values at runtime. Like in a Smalltalk environment the inspect
    features an evaluation pane into which you can type in arbitrary
    JavaScript code and evaluate it in the context of the inspectee.

    Use switching between user and development modes while you are
    developing an application and disable switching to development once
    you're done and deploying, because generally you don't want to
    confuse end-users with inspectors and meta-level stuff.


    (7) turtle graphics
    -------------------

    The basic Morphic kernel features a simple LOGO turtle constructor
    called

        PenMorph

    which you can use to draw onto its parent Morph. By default every
    Morph in the system (including the World) is able to act as turtle
    canvas and can display pen trails. Pen trails will be lost whenever
    the trails morph (the pen's parent) performs a "render()"
    operation. If you want to create your own pen trails canvas, you
    may wish to modify its

        penTrails()

    property, so that it keeps a separate offscreen canvas for pen
    trails (and doesn't loose these on redraw).

    the following properties of PenMorph are relevant for turtle
    graphics:

        color       - a Color
        size        - line width of pen trails
        heading     - degrees
        isDown      - drawing state

    the following commands can be used to actually draw something:

        up()        - lift the pen up, further movements leave no trails
        down()      - set down, further movements leave trails
        clear()     - remove all trails from the current parent
        forward(n)  - move n steps in the current direction (heading)
        turn(n)     - turn right n degrees

    Turtle graphics can best be explored interactively by creating a
    new PenMorph object and by manipulating it with the inspector
    widget.

    NOTE: PenMorph has a special optimization for recursive operations
    called

        warp(function)

    You can significantly speed up recursive ops and increase the depth
    of recursion that's displayable by wrapping WARP around your
    recursive function call:

    example:

        myPen.warp(function () {
            myPen.tree(12, 120, 20);
        })

    will be much faster than just invoking the tree function, because it
    prevents the parent's parent from keeping track of every single line
    segment and instead redraws the outcome in a single pass.


    (8) supporting high-resolution "retina" screens
    -----------------------------------------------
    By default retina support gets installed when Morphic.py loads. There
    are two global functions that let you test for retina availability:

        isRetinaSupported() - Bool, answers if retina support is available
        isRetinaEnabled()   - Bool, answers if currently in retina mode

    and two more functions that let you control retina support if it is
    available:

        enableRetinaSupport()
        disableRetinaSupport()

    Both of these internally test whether retina is available, so they are
    safe to call directly. For an example how to make retina support
    user-specifiable refer to

        Snap! >> guis.py >> toggleRetina()

    Even when in retina mode it often makes sense to use normal-resolution
    canvasses for simple shapes in order to save system resources and
    optimize performance. Examples are costumes and backgrounds in Snap.
    In Morphic you can create new canvas elements using

        newCanvas(extentPoint [, nonRetinaFlag])

    If retina support is enabled such new canvasses will automatically be
    high-resolution canvasses, unless the newCanvas() function is given an
    otherwise optional second Boolean <true> argument that explicitly makes
    it a non-retina canvas.

    Not the whole canvas API is supported by Morphic's retina utilities.
    Especially if your code uses putImageData() you will want to "downgrade"
    a target high-resolution canvas to a normal-resolution ("non-retina")
    one before using

        normalizeCanvas(aCanvas [, copyFlag])

    This will change the target canvas' resolution in place (!). If you
    pass in the optional second Boolean <true> flag the function returns
    a non-retina copy and leaves the target canvas unchanged. An example
    of this normalize mechanism is converting the penTrails layer of Snap's
    stage (high-resolution) into a sprite-costume (normal resolution).


    (9) animations
    ---------------
    Animations handle gradual transitions between one state and another over a
    period of time. Transition effects can be specified using easing functions.
    An easing function maps a fraction of the transition time to a fraction of
    the state delta. This way accelerating / decelerating and bouncing sliding
    effects can be accomplished.

    Animations are generic and not limited to motion, i.e. they can also handle
    other transitions such as color changes, transparency fadings, growing,
    shrinking, turning etc.

    Animations need to be stepped by a scheduler, e. g. an interval function.
    In Morphic the preferred way to run an animation is to register it with
    the World by adding it to the World's animation queue. The World steps each
    registered animation once per display cycle independently of the Morphic
    stepping mechanism.

    For an example how to use animations look at how the Morph's methods

        glideTo()
        fadeTo()

    and

        slideBackTo()

    are implemented.


    (10) minifying morphic.py
    -------------------------
    Coming from Smalltalk and being a Squeaker at heart I am a huge fan
    of browsing the code itself to make sense of it. Therefore I have
    included this documentation and (too little) inline comments so all
    you need to get going is this very file.

    Nowadays with live streaming HD video even on mobile phones 250 KB
    shouldn't be a big strain on bandwith, still minifying and even
    compressing morphic.py down do about 100 KB may sometimes improve
    performance in production use.

    Being an attorney-at-law myself you programmer folk keep harassing
    me with rabulistic nitpickings about free software licenses. I'm
    releasing morphic.py under an AGPL license. Therefore please make
    sure to adhere to that license in any minified or compressed version.


    VIII. acknowledgements
    ----------------------
    The original Morphic was designed and written by Randy Smith and
    John Maloney for the SELF programming language, and later ported to
    Squeak (Smalltalk) by John Maloney and Dan Ingalls, who has also
    ported it to JavaScript (the Lively Kernel), once again setting
    a "Gold Standard" for self sustaining systems which morphic.py
    cannot and does not aspire to meet.

    This Morphic implementation for JavaScript is not a direct port of
    Squeak's Morphic, but still many individual functions have been
    ported almost literally from Squeak, sometimes even including their
    comments, e.g. the morph duplication mechanism fullCopy(). Squeak
    has been a treasure trove, and if morphic.py looks, feels and
    smells a lot like Squeak, I'll take it as a compliment.

    Evelyn Eastmond has inspired and encouraged me with her wonderful
    implementation of DesignBlocksJS. Thanks for sharing code, ideas
    and enthusiasm for programming.

    John Maloney has been my mentor and my source of inspiration for
    these Morphic experiments. Thanks for the critique, the suggestions
    and explanations for all things Morphic and for being my all time
    programming hero.

    I have originally written morphic.py in Florian Balmer's Notepad2
    editor for Windows, later switched to Apple's Dashcode and later
    still to Apple's Xcode. I've also come to depend on both Douglas
    Crockford's JSLint and later the JSHint project, as well as on
    Mozilla's Firebug and Google's Chrome to get it right.


    IX. contributors
    ----------------------
    Joe Otto found and fixed many early bugs and taught me some tricks.
    Nathan Dinsmore contributed mouse wheel scrolling, cached
    background texture handling, countless bug fixes and optimizations.
    Ian Reynolds contributed backspace key handling for Chrome.
    Davide Della Casa contributed performance optimizations for Firefox.
    Jason N (@cyderize) contributed native copy & paste for text editing.
    Bartosz Leper contributed retina display support.
    Zhenlei Jia and Dariusz Dorożalski pioneered IME text editing.
    Bernat Romagosa contributed to text editing and to the core design.
    Michael Ball found and fixed a longstanding scrolling bug.
    Brian Harvey contributed to the design and implementation of submenus.
    Ken Kahn contributed to Chinese keboard entry and Android support.
    Brian Broll contributed clickable URLs in text elements and many bugfixes.

    - Jens Mönig
'''

import math
import re
import tkinter
import time

## Global settings #####################################################

'''global window, HTMLCanvasElement, FileReader, Audio, FileList, Map'''

'''pyhint esversion: 6'''

morphicVersion = '2021-December-06'
modules = {} # keep track of additional loaded modules
useBlurredShadows = True

ZERO = Point()
BLACK = Color()
WHITE = Color(255, 255, 255)
CLEAR = Color(0, 0, 0, 0)

standardSettings = {
    "minimumFontHeight": getMinimumFontHeight(), # browser settings
    "globalFontFamily": '',
    "menuFontName": 'sans-serif',
    "menuFontSize": 12,
    "bubbleHelpFontSize": 10,
    "prompterFontName": 'sans-serif',
    "prompterFontSize": 12,
    "prompterSliderSize": 10,
    "handleSize": 15,
    "scrollBarSize": 9, # was 12,
    "mouseScrollAmount": 40,
    "useSliderForInput": False,
    "isTouchDevice": False, # turned on by touch events, don't set
    "rasterizeSVGs": False,
    "isFlat": False,
    "grabThreshold": 5,
    "showHoles": False
}

touchScreenSettings = {
    "minimumFontHeight": standardSettings.minimumFontHeight,
    "globalFontFamily": '',
    "menuFontName": 'sans-serif',
    "menuFontSize": 24,
    "bubbleHelpFontSize": 18,
    "prompterFontName": 'sans-serif',
    "prompterFontSize": 24,
    "prompterSliderSize": 20,
    "handleSize": 26,
    "scrollBarSize": 24,
    "mouseScrollAmount": 40,
    "useSliderForInput": False,
    "isTouchDevice": True,
    "rasterizeSVGs": False,
    "isFlat": False,
    "grabThreshold": 5,
    "showHoles": False
}

MorphicPreferences = standardSettings

## Global Functions ########################################################

def nop():
    # do explicitly nothing
    pass

def localize(string):
    # override this function with custom localizations
    return string

def isNil(thing):
    return thing is None

def contains(list, element):
    # answer true if element is a member of list
    return element in list

def detect(list, predicate):
    # answer the first element of list for which predicate evaluates
    # True, otherwise answer None
    for i in list:
        if predicate(i):
            return i
    return None

def sizeOf(object):
    # answer the number of own properties
    return len(dir(object))

def isString(target):
    return isinstance(target, str)

def isObject(target):
    return target is not None and isinstance(target, object)

def radians(degrees):
    return degrees*math.pi/180

def degrees(radians):
    return radians*180/math.pi

def fontHeight(height):
    minheight = max(height, MorphicPreferences.minimumFontHeight)
    return minheight * 1.2 # assuming 1/5 font size for ascenders

def isWordChar(aCharacter):
    # can't use \b or \w because they ignore diacritics
    return re.match(r"[A-zÀ-ÿ0-9]", aCharacter)

def isURLChar(aCharacter):
    return re.match(r"[A-z0-9./:?&_+%-]", aCharacter)

def isURL(text):
    return re.match(r"^https?://", text)

def newCanvas(extentPoint=None, recycleMe=None):
    if isNil(extentPoint):
        ext = (math.ceil(Point(recycleMe.width, recycleMe.height) if
               not isNil(recycleMe) else Point(0, 0)))
    else:
        ext = extentPoint
    if (not isNil(recycleMe) and
        not recycleMe.dataset.morphicShare and
        ext.x == recycleMe.width and ext.y == recycleMe.height):
        canvas = recycleMe
        canvas.delete("all")
    else:
        canvas = tkinter.Canvas(width=ext.x, height=ext.y)
    return canvas

'''
def copyCanvas(aCanvas=None):
    if (not isNil(aCanvas) and
        hasattr(aCanvas, "width") and
        hasattr(aCanvas, "height")):
        c = newCanvas(
            Point(aCanvas.width, aCanvas.height)
        )
        c.create_image(0, 0, image=aCanvas)
'''

def getMinimumFontHeight():
    return 1

def getDocumentPositionOf(aDOMelement):
    return {"x": 0, "y": 0}

def copy(target):
    from copy import copy
    aCopy = copy(target)
    del copy
    return aCopy

# Animations ###############################################################

'''
    Animations handle gradual transitions between one state and another over
    a period of time. Transition effects can be specified using easing
    functions. An easing function maps a fraction of the transition time to
    a fraction of the state delta. This way accelerating / decelerating and
    bouncing sliding effects can be accomplished.

    Animations are generic and not limited to motion, i.e. they can also
    handle other transitions such as color changes, transparency fadings,
    growing, shrinking, turning etc.

    Animations need to be stepped by a scheduler, e. g. an interval
    function. In Morphic the preferred way to run an animation is to
    register it with the World by adding it to the World's animation queue.
    The World steps each registered animation once per display cycle
    independently of the Morphic stepping mechanism.

    For an example how to use animations look at how the Morph's methods

        glideTo()
        fadeTo()

    and

        slideBackTo()

    are implemented.
'''

class Animation:

    # Animation instance creation:

    def __init__(self, setter, getter,
                 delta=0, duration=0,
                 easing=None, onComplete=None):
        self.easings = {
            # dictionary of a few pre-defined easing functions used to
            # transition two states

            # ease both in and out:
            "linear": lambda t: t,
            "sinusoidal": lambda t: 1-math.cos(radians(t*90)),
            "quadratic": lambda t: (2*t**2 if t<1/2 else 4*t-2*t**2-1),
            "cubic": lambda t: (4*t**3 if t<1/2 else (t-1)*4*t**2-8*t-3),
            "elastic": lambda t: ((math.sin(50*t))/100+
                                  (math.sin(50*t))/(100*t) if t<1/2
                                  else (math.sin(50*t))/50-
                                       (math.sin(50*t))/(100*t)+1),

            # ease in only:
            "sine_in": lambda t: 1-math.sin(radians(90+(t*90))),
            "quad_in": lambda t: t**2,
            "cubic_in": lambda t: t**3,
            "elastic_in": lambda t: (1/25-1/(25*t))*math.sin(25*t)+1,

            # ease out only:
            "sine_out": lambda t: math.sin(radians(t*90)),
            "quad_out": lambda t: t*(2-t),
            "elastic_out": lambda t: t/(25*(t-1))*math.sin(25*t)
        }
        self.setter = setter # function
        self.getter = getter # function
        self.delta = delta # number
        self.duration = duration # milliseconds
        if isString(easing): # string or function
            if easing in self.easings:
                self.easing = self.easings[easing]
            else:
                self.easing = self.easings.sinusoidal
        else:
            if not isNil(easing):
                self.easing = easing
            else:
                self.easing = self.easings.sinusoidal
        self.onComplete = onComplete # optional callback
        self.endTime = None
        self.destination = None
        self.isActive = False
        self.start()

    def start(self):
        # (re-) activate the animation, e.g. if is has previously completed,
        # make sure to plug it into something that repeatedly triggers
        # step(), e.g. the World's animations queue
        self.endTime = time.time_ns()//1000000
        self.destination = self.getter(self) + self.delta
        self.isActive = True

    def step(self):
        if not self.isActive: return
        now = time.time_ns()//1000000
        if now > self.endTime:
            self.setter(self.destination)
            self.isActive = False
            if not isNil(self.onComplete): self.onComplete()
        else:
            self.setter(
                self.destination -
                self.delta*self.easing((self.endTime-now)/self.duration)
            )

# Colors ###################################################################

class Color:

    # Color instance creation:

    def __init__(self, r=0, g=0, b=0, a=1):
        # all values are optional, just (r, g, b) is fine
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.a = int(a)

    # Color string representation: e.g. 'Color(255, 165, 0, 1)'
    def __repr__(self):
        return (
            'Color(' +
            self.r + ', ' +
            self.g + ', ' +
            self.b + ', ' +
            self.a + ')'
        )

    @classmethod
    def fromString(cls, aString):
        # I parse rgb/rgba strings into a Color object
        components = re.split(r"[\(), ]", aString)[1:5]
        return Color(*components)

    # Color copying:
    def copy(self):
        return Color(
            self.r,
            self.g,
            self.b,
            self.a
        )

    # Color comparison:
    def __eq__(self, other):
        return (
            isinstance(other, Color) and
            self.r == other.r and
            self.g == other.g and
            self.b == other.b and
            self.a == other.a
        )

    def isCloseTo(self, other, tolerance=10):
        # experimental - answer whether a color is "close" to another one by
        # a given percentage. tolerance is the percentage by which each
        # color channel may diverges
        threshold = 64/25 * tolerance

        def dist(a, b):
            return abs(a-b)

        return (
            isinstance(other, Color) and
            dist(self.r, other.r) < threshold and
            dist(self.g, other.g) < threshold and
            dist(self.b, other.b) < threshold and
            dist(self.a, other.a) < threshold
        )

    # Color conversion (hsva):
    @classmethod
    def rgba_hsva(cls, r=0, g=0, b=0, a=1):
        rr = r/255
        gg = g/255
        bb = b/255
        max_ = max(rr, gg, bb)
        min_ = min(rr, gg, bb)
        h = max_
        s = max_
        v = max_
        d = max_ - min_
        s = 0 if max_ == 0 else d/max_
        if max_ == min_:
            h = 0
        else:
            if max == rr:
                h = (gg-bb)/d+(6 if gg<bb else 0)
            elif max_ == gg:
                h = (bb-rr)/d+2
            elif max_ == bb:
                h = (rr-gg)/d+4
            else:
                raise Exception("This error should never be raised. "
                                "Please report this as a bug.")
            h /= 6
        return (h, s, v, a)

    @classmethod
    def hsva_rgba(cls, h=0, s=0, v=0, a=1):
        # h, s, v, and a are to be within [0, 1]
        i = math.floor(h*6)
        f = h*6-i
        p = v*(1-s)
        q = v*(1-f*s)
        t = v*(1-(1-f)*s)
        imod6 = i % 6
        if imod6 == 0:
            r = v
            g = t
            b = p
        elif imod6 == 1:
            r = q
            g = v
            b = p
        elif imod6 == 2:
            r = p
            g = v
            b = t
        elif imod6 == 3:
            r = p
            g = q
            b = v
        elif imod6 == 4:
            r = t
            g = p
            b = v
        elif imod6 == 5:
            r = v
            g = p
            b = q
        else:
            raise Exception("This error should never be raised. "
                            "Please report this as a bug.")
        return (r*255, g*255, b*255, a)

    # Color conversion (hsla):
    @classmethod
    def rgba_hsla(cls, r=0, g=0, b=0, a=1):
        rr = r/255
        gg = g/255
        bb = b/255
        max_ = max(rr, gg, bb)
        min_ = min(rr, gg, bb)
        l = (max_+min_)/2
        if max_ == min_: # achromatic
            h = 0
            s = 0
        else:
            d = max_-min_
            s = d/(2-max_-min_) if l>1/2 else d/(max_+min_)
            if max_ == rr:
                h = (gg-bb)/d+(6 if gg<bb else 0)
            elif max_ == gg:
                h = (bb-rr)/d+2
            elif max_ == bb:
                h = (rr-gg)/d+4
            h /= 6
        return (h, s, l, a)

    @classmethod
    def hsla_rgba(cls, h=0, s=0, l=0, a=1):
        # h, s, l, and a are to be within [0, 1]
        def hue_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p+(q-p)*6*t
            if t < 1/2:
                return q
            if t < 2/3:
                return p+(q-p)*(2/3-t)*6
            return p
        if s == 0: # achromatic
            r = 1
            g = 1
            b = 1
        else:
            q = l*(1+s) if l<1/2 else l+s-l*s
            p = 2*l-q
            r = hue_rgb(p, q, h+1/3)
            g = hue_rgb(p, q, h)
            b = hue_rgb(p, q, h-1/3)
        return (r*255, g*255, b*255, a)

    # Color mixing:
    def mixed(self, proportion, otherColor):
        # answer a copy of this color mixed with another color
        if not isinstance(otherColor, Color): return self
        frac1 = min(max(proportion, 0), 1)
        frac2 = 1 - frac1
        return Color(
            self.r * frac1 + otherColor.r * frac2,
            self.g * frac1 + otherColor.g * frac2,
            self.b * frac1 + otherColor.b * frac2,
            self.a * frac1 + otherColor.a * frac2
        )

    def darker(self, percent=None):
        # return an rgb-interpolated darker copy of me
        fract = 74/90 # 0.8333...
        if not isNil(percent):
            fract = (100-percent)/100
        return self.mixed(fract, BLACK)

    def lighter(self, percent=None):
        # return an rgb-interpolated lighter copy of me
        fract = 74/90 # 0.8333...
        if not isNil(percent):
            fract = (100-percent)/100
        return self.mixed(fract, WHITE)

    def dansDarker(self, percent=16):
        # return an rgb-interpolated darker copy of me
        hsva = list(Color.rgba_hsva(
            self.r,
            self.g,
            self.b,
            self.a
        ))
        hsva[2] = max(hsva[2]-percent/100, 0)
        result = Color(*Color.hsva_rgba(*hsva))
        return result

    def inverted(self):
        return Color(
            255-self.r,
            255-self.g,
            255-self.b,
            1-self.a
        )

    def solid(self):
        return Color(
            self.r,
            self.g,
            self.b
        )

# Points ###################################################################

class Point:

    # Point instance creation:

    def __init__(self, x=0, y=0):
        self.x = int(float(x))
        self.y = int(float(y))

    # Point string representation:

    # repr, e.g. 'Point(12, 68)'
    def __repr__(self):
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"

    # str, e.g. '12@68'
    def __str__(self):
        return str(self.x) + "@" + str(self.y)

    # Point copying:
    def copy(self):
        return Point(self.x, self.y)

    # Point comparison:
    def __eq__(self, other):
        return (
            isinstance(other, Point) and
            self.x == other.x and
            self.y == other.y
        )

    def __lt__(self, other):
        return (
            isinstance(other, Point) and
            self.x < other.x and
            self.y < other.y
        )

    def __gt__(self, other):
        return (
            isinstance(other, Point) and
            self.x > other.x and
            self.y > other.y
        )

    def __ge__(self, other):
        return (
            isinstance(other, Point) and
            self.x >= other.x and
            self.y >= other.y
        )

    def __le__(self, other):
        return (
            isinstance(other, Point) and
            self.x <= other.x and
            self.y <= other.y
        )

    def max(self, other):
        if isinstance(other, Point):
            return Point(
                max(self.x, other.x),
                max(self.y, other.y)
            )
        return self

    def min(self, other):
        if isinstance(other, Point):
            return Point(
                min(self.x, other.x),
                min(self.y, other.y)
            )
        return self

    # Point conversion:
    def __round__(self, ndigits=0):
        return Point(
            round(self.x, ndigits),
            round(self.y, ndigits)
        )

    def __abs__(self):
        return Point(
            abs(self.x),
            abs(self.y)
        )

    def __neg__(self):
        return Point(
            -self.x,
            -self.y
        )

    def mirror(self, axis=None):
        if not isinstance(axis, Point):
            axis = Point(1, 1)
        axis = abs(axis)
        vx, vy = axis.asTuple
        x, y = -self.asTuple
        r = 1/axis.dot(axis)
        return Point(
            self.x+2*(x-(x*vx-y*vy)*r*vx),
            self.y+2*(y-(y*vy-x*vx)*r*vy)
        )

    def __floor__(self):
        return Point(
            math.floor(self.x),
            math.floor(self.y)
        )

    def __ceil__(self):
        return Point(
            math.ceil(self.x),
            math.ceil(self.y)
        )

    # Point arithmetic:
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x+other.x, self.y+other.y)
        return Point(self.x+other, self.y+other)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x-other.x, self.y-other.y)
        return Point(self.x-other, self.y-other)

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x*other.x, self.y*other.y)
        return Point(self.x*other, self.y*other)

    def __truediv__(self, other):
        if isinstance(other, Point):
            return Point(self.x/other.x, self.y/other.y)
        return Point(self.x/other, self.y/other)

    __div__ = __truediv__

    def __floordiv__(self, other):
        if isinstance(other, Point):
            return Point(self.x//other.x, self.y//other.y)
        return Point(self.x//other, self.y//other)

    def __mod__(self, other):
        if isinstance(other, Point):
            return Point(self.x%other.x, self.y%other.y)
        return Point(self.x%other, self.y%other)

    def __radd__(self, other):
        if isinstance(other, Point):
            return Point(self.x+other.x, self.y+other.y)
        return Point(self.x+other, self.y+other)

    def __rsub__(self, other):
        if isinstance(other, Point):
            return Point(other.x-self.x, other.y-self.y)
        return Point(other-self.x, other-self.y)

    def __rmul__(self, other):
        if isinstance(other, Point):
            return Point(other.x*self.x, other.y*self.y)
        return Point(other*self.x, other*self.y)

    def __rtruediv__(self, other):
        if isinstance(other, Point):
            return Point(other.x/self.x, other.y/self.y)
        return Point(other/self.x, other/self.y)

    __rdiv__ = __rtruediv__

    def __rfloordiv__(self, other):
        if isinstance(other, Point):
            return Point(other.x//self.x, other.y//self.y)
        return Point(other//self.x, other//self.y)

    def __rmod__(self, other):
        if isinstance(other, Point):
            return Point(other.x%self.x, other.y%self.y)
        return Point(other%self.x, other%self.y)

    # Point polar coordinates:
    @property
    def r(self):
        return math.sqrt(self.dot(self))

    @property
    def theta(self):
        if self.x == 0:
            if self.y == 0:
                return 0
            return 90
        return degrees(math.atan(self.y/self.x))

    @classmethod
    def theta_r_to_x_y(cls, theta, r):
        return Point(
            math.cos(theta),
            math.sin(theta)
        ) * r

    # Point functions:
    def __cross__(self, other):
        if isinstance(other, Point):
            stom = self * other.mirror()
            return stom.x-stom.y
        return NotImplemented

    cross = __cross__

    def __dot__(self, other):
        if isinstance(other, Point):
            sto = self * other
            return sto.x + sto.y
        return NotImplemented

    dot = __dot__

    def distanceTo(self, other):
        return (other-self).r

    def rotate(self, amount):
        return Point.theta_r_to_x_y(self.theta + amount, self.r)

    flip = mirror

    # I don't know what this does.
    def distanceAngle(self, dist, angle):
        deg = angle
        while not -270 < deg < 270:
            if deg > 270:
                deg -= 360
            elif deg < -270:
                deg += 360
        if -90 <= deg <= 90:
            x = math.sin(radians(deg)) * dist
            y = Point(dist, x).r
            return Point(x + self.x, y - self.y)
        x = math.sin(radians(180 - deg)) * dist
        y = Point(dist, x).r
        return Point(x + self.x, y + self.y)

    # Point transformation:
    def scale(self, scale):
        return self * scale

    def translate(self, delta):
        return self + delta

    # Point conversion:
    @property
    def asTuple(self):
        return self.x, self.y

    @property
    def asList(self):
        return [self.x, self.y]

    def __iter__(self):
        yield self.x
        yield self.y
