import sys

sys.dont_write_bytecode = True

import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.dates as mdates
import pandas as pd


def generate_calorie_chart_pdf(dataframe):
    """
    Generate a PDF report with a calorie intake chart.

    Args:
        dataframe (pandas.DataFrame): DataFrame containing calorie intake data.

    Returns:
        bytes: The PDF content as bytes.
    """
    # Sort DataFrame by date
    dataframe = dataframe.sort_values("Date").reset_index(drop=True)

    # Convert date column to datetime format
    dataframe["Date"] = pd.to_datetime(dataframe["Date"]).dt.date

    # Create a buffer to hold the PDF content
    buffer = io.BytesIO()

    # Create a PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create a table object
    data = [dataframe.columns] + dataframe.values.tolist()
    table = Table(data)

    # Apply styles to the table
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), "grey"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), "lightgrey"),
                ("GRID", (0, 0), (-1, -1), 1, "black"),
            ]
        )
    )

    # Plot the line chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dataframe["Date"], dataframe["Calories"], color="blue")

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories")
    ax.set_title("Calorie Intake Report")

    # Set the date format for the x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    # Set the frequency of the date ticks to show every 10 days
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))

    # Determine the number of x-axis labels
    num_labels = len(ax.get_xticks())

    # Adjust the image size based on the number of x-axis labels
    img_width = 6 + (num_labels * 0.2)  # Adjust this value as needed
    img_height = 4
    fig.set_size_inches(img_width, img_height)

    # Convert the plot to an image
    canvas = FigureCanvas(fig)
    img_data = io.BytesIO()
    canvas.print_png(img_data)
    img_data.seek(0)

    # Add the plot image to the PDF
    img = Image(img_data)
    img._restrictSize(img_width * 72, img_height * 72)
    pdf_content = [
        Paragraph("Calorie Intake Report", styles["Title"]),
        table,
        img,
    ]
    pdf.build(pdf_content)

    # Close the plot
    plt.close()

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the PDF content as bytes
    return buffer.read()
