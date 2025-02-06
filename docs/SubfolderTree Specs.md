# Overview

SubfolderTree is a graphical user interface (GUI) application designed to provide users with a simple yet powerful method of visualizing and interacting with their directory structures. The application enables users to seamlessly navigate through their file systems, inspect folder contents, and generate a text-based, ASCII representation of the folder hierarchy. By combining advanced features like dynamic sorting, interactive column resizing, and real-time directory scanning, SubfolderTree offers a robust solution for managing and documenting file systems across platforms.

# Features

SubfolderTree offers a variety of features that cater to both casual users and advanced file system enthusiasts:

- **Interactive Tree View:**  
  The core component of the application is a dual-column tree view. The left column displays file and folder names while the right column shows corresponding file sizes. The design ensures that the "Name" column stretches automatically to fill available space, whereas the "Size" column maintains a fixed width of 80 pixels, although it remains manually adjustable.

- **Folder Navigation:**  
  Users can easily navigate deeper into subfolders by double-clicking on any folder entry in the tree view. Additionally, a dedicated parent folder navigation button allows users to move back up the directory hierarchy quickly, ensuring that exploration remains fluid and intuitive.

- **ASCII Tree Generation:**  
  One of the standout features of SubfolderTree is its ability to generate an ASCII representation of the folder structure. This feature creates a compact, readable tree diagram using textual connectors (e.g. "├─", "└─", "│") that clearly delineate folder levels. Users have the option to copy this ASCII tree to their clipboard for documentation or sharing purposes.

- **Background Directory Scanning:**  
  To enhance performance, the application leverages a background thread for scanning directory contents. This means that even large file systems can be traversed without freezing the user interface, while users are kept informed through a responsive progress indicator.

- **Sorting and Resizing:**  
  The header of the tree view facilitates sorting based on name or file size with a simple click, and the columns themselves are designed to be interactive. This leads to a highly customizable view where users can tweak the interface to best fit their needs.

# Layout Components

The layout of SubfolderTree is divided into three primary sections:

- **Top Row:**  
  The top row houses various controls, including a folder selection button, a parent folder navigation button, and a text field that displays the current directory path. This section also contains buttons for reloading and deleting contents, providing quick access to essential file operations.

- **Middle Row:**  
  Dominated by the interactive tree view, the middle section is where the file system hierarchy is presented. The left column dynamically fills the available space with file and folder names, while the right column, showing file sizes, remains fixed at 80 pixels. This design ensures a clear, organized presentation of directory contents.

- **Bottom Row:**  
  The bottom row offers additional functionality such as moving selected items between panes and generating an ASCII tree of the folder structure. This section is designed to provide users with extra options for managing and documenting their files.

# ASCII Tree Generation

A notable component of SubfolderTree is its capability to generate an ASCII tree that represents the directory structure. This feature works as follows:

1. **Recursive Traversal:**  
   When activated, the application recursively scans through subfolders and files of the selected directory, constructing a nested representation of the file system.

2. **Visual Formatting:**  
   The algorithm uses a set of textual connectors like "├─", "└─", and "│" combined with careful spacing to compartmentalize each level of the hierarchy. Adjustments in the connector and indentation logic ensure that the sub-tree lines align neatly with the first character of the parent folder name, resulting in a compact and visually appealing output.

3. **User-Centric Selection:**  
   The ASCII tree generation considers only the items selected by the user in the tree view. This focus allows the output to be precise and tailored, ensuring that only relevant sections of the folder structure are included. The final ASCII output can be easily copied to the clipboard, making it useful for documentation, presentations, or further processing.

Overall, SubfolderTree combines an intuitive user interface with powerful file system management features. Its ability to visualize the hierarchy both graphically and textually makes it a versatile and valuable tool for those who manage complex directory structures.



