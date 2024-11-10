import plotly.express as px
from shiny.express import input, ui
from shiny import render, reactive
from shinywidgets import render_widget, render_plotly
import palmerpenguins  # This package provides the Palmer Penguins dataset
from shinyswatch import theme
import seaborn as sns

# Use the built-in function to load the Palmer Penguins dataset
from palmerpenguins import load_penguins 
penguins = load_penguins()

ui.page_opts(title="Melissa's Palmer's Penguin Data Review", fillable=True, theme=theme.morph)

# Add a Shiny UI sidebar for user interaction
# Use a with block to add content to the sidebar
with ui.sidebar(bg="#8fb597"):  
    ui.h2("Sidebar") # Use the ui.h2() function to add a 2nd level header to the sidebar    
    ui.div(
        ui.hr(),  # Use ui.hr() to add a horizontal rule to the sidebar 
        style="border-top: 2px solid #495569; margin: 10px 0;"  # Custom style for the horizontal rule
    ) 

    # Use ui.input_checkbox_group() to create a checkbox group input to filter the species
    ui.input_checkbox_group(  
        "selected_species_list",  
        "Select One or More Species:",
        choices=["Adelie", "Chinstrap", "Gentoo"],
        selected=["Adelie", "Chinstrap", "Gentoo"],
        inline=False 
    )

    # Use ui.input_checkbox_group() to create a checkbox group input to filter the island
    ui.input_checkbox_group(  
        "selected_island_list",  
        "Select One or More Islands:",
        choices=["Biscoe", "Dream", "Torgersen"],
        selected=["Biscoe", "Dream", "Torgersen"],
        inline=False 
    )

    ui.div(
        ui.hr(),  # Use ui.hr() to add a horizontal rule to the sidebar 
        style="border-top: 2px solid #495569; margin: 10px 0;"  # Custom style for the horizontal rule
    )  
    
    # Use ui.input_numeric() to create a numeric input for the number of Plotly histogram bins
    ui.input_numeric("plotly_bin_count", "Plotly Bin Count", 20, min=1, max=100)  

    @render.text
    def numeric():
        return input.numeric()

    ui.div(
        ui.hr(),  # Use ui.hr() to add a horizontal rule to the sidebar 
        style="border-top: 2px solid #495569; margin: 10px 0;"  # Custom style for the horizontal rule
    ) 
    
    # Use ui.input_slider() to create a slider input for the number of Seaborn bin
    (ui.input_slider("seaborn_bin_count", "Seaborn Bin Count", 1, 50, 25),)  

    @render.text
    def slider():
        return f"{input.slider()}"
  
    @render.text
    def value():
        return ", ".join(input.checkbox_group())

    ui.div(
        ui.hr(),  # Use ui.hr() to add a horizontal rule to the sidebar 
        style="border-top: 2px solid #495569; margin: 10px 0;"  # Custom style for the horizontal rule
    )
    ui.h4("Interactive Scatterplot")
    
    # Dropdown for selecting x and y axes for the scatter plot
    ui.input_selectize("x_column_scatter", "Select X Variable:", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
    ui.input_selectize("y_column_scatter", "Select Y Variable:", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
    
    @render.text
    def select():
        return f"{input.selectize()}"   
        
    # Use ui.a() to add a hyperlink to the sidebar
    ui.a("Melissa's GitHub", href="https://github.com/meldstonerogers", target="_blank") 

#####Main Content##### 
#Data Table, showing all data
#Data Grid, showing all data

with ui.layout_columns():
    with ui.card(full_screen=True):
            ui.card_header("Data Table")
            
            @render.data_frame  
            def plot1():
                return (filtered_data())

    with ui.card(full_screen=True):
            ui.card_header("Data Grid")
        
            @render.data_frame  
            def plot2():
                return (filtered_data())

with ui.layout_columns():
    #Plotly Histogram, showing all species 
    with ui.card(full_screen=True):
            ui.card_header("Plotly Histogram")
            @render_widget  
            def plot3():  
                penguins = filtered_data()
                histogram = px.histogram(
                    penguins,
                    x="body_mass_g",
                    nbins=input.plotly_bin_count(),
                    color="species",
                ).update_layout(
                    title={"text": "Penguin Mass", "x": 0.5},
                    yaxis_title="Count",
                    xaxis_title="Body Mass (g)",
                )  
                return histogram

    #Seaborn Histogram, showing all species 
    with ui.card(full_screen=True):
            ui.card_header("Seaborn Histogram")
            @render.plot(alt="A Seaborn histogram on penguin body mass in grams.")  
            def plot4():
                penguins = filtered_data()
                ax = sns.histplot(
                    data = filtered_data(), 
                    x="body_mass_g", 
                    bins=input.seaborn_bin_count(), 
                    hue="species",
                    kde=False,)  
                ax.set_title("Penguins Mass")
                ax.set_xlabel("Mass (g)")
                ax.set_ylabel("Count")
                return ax 

#Plotly Scatterplot, showing all species 
with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot: Species")
    @render_widget 
    def penguins_scatter_plot():  
        x_column_name = input.x_column_scatter()
        y_column_name = input.y_column_scatter()

        # Filter the penguins dataset based on selected species
        penguins = filtered_data()

        # Create scatter plot
        scatterplot = px.scatter(
            data_frame = filtered_data(),
            x=x_column_name,  # X-axis based on user selection
            y=y_column_name,  # Y-axis based on user selection
            color="species",  # Color points by species
            title=f"{x_column_name} vs {y_column_name}",
            labels={x_column_name: x_column_name, y_column_name: y_column_name}  # Custom labels for axes
        ).update_layout(
            title={"text": f"{x_column_name} vs {y_column_name}", "x": 0.5},
            yaxis_title=y_column_name,
            xaxis_title=x_column_name,
        )

        return scatterplot

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

# Define server logic
    @reactive.calc
    def filtered_data():
        isFilterMatch = (
            penguins["species"].isin(input.selected_species_list()) & 
            penguins["island"].isin(input.selected_island_list())
        )    
        return penguins[isFilterMatch]
