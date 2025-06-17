import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

# Set up the app
st.set_page_config(page_title="Volatility Surface Explorer", layout="wide")
st.title("📊 Volatility Surface Explorer")

# Sidebar for user inputs
with st.sidebar:
    st.header("Input Parameters")
    ticker = st.text_input("Ticker Symbol", value="SPY")
    interpolation_method = st.selectbox(
        "Interpolation Method",
        options=['cubic', 'linear', 'nearest'],
        index=0
    )
    generate_btn = st.button("Generate Volatility Surface")

# Main content area
main_container = st.container()

# Placeholder for the plot
plot_placeholder = st.empty()

# Sample data function (replace with real data fetching)
def get_sample_data(ticker):
    """Generate sample volatility surface data"""
    strikes = np.array([80, 90, 100, 110, 120])
    expiries = np.array([0.1, 0.5, 1.0, 1.5, 2.0])
    iv = np.array([0.25, 0.22, 0.20, 0.23, 0.26])  # Sample implied volatilities
    
    # Create more sample points for better visualization
    rng = np.random.default_rng(42)
    num_points = 20
    strikes = rng.uniform(75, 125, num_points)
    expiries = rng.uniform(0.1, 2.0, num_points)
    iv = 0.2 + 0.1 * np.sin(strikes/20) * np.cos(expiries)
    
    return strikes, expiries, iv

# Create interpolation grid (from first function)
def create_3d_interpolation_grid(strikes, expiries, values, method='cubic'):
    try:
        strikes = np.asarray(strikes, dtype=float)
        expiries = np.asarray(expiries, dtype=float)
        values = np.asarray(values, dtype=float)
        
        grid_x, grid_y = np.mgrid[
            min(strikes):max(strikes):100j,
            min(expiries):max(expiries):100j
        ]
        
        points = np.column_stack((strikes, expiries))
        grid_z = griddata(points, values, (grid_x, grid_y), method=method)
        
        # Handle NaN values
        if np.any(np.isnan(grid_z)):
            grid_z = griddata(points, values, (grid_x, grid_y), method='linear')
            if np.any(np.isnan(grid_z)):
                grid_z = griddata(points, values, (grid_x, grid_y), method='nearest')
        
        return grid_x, grid_y, grid_z
    except Exception as e:
        st.error(f"Interpolation error: {str(e)}")
        return None, None, None

# Create Plotly figure (from second function)
def create_plotly_figure(grid_x, grid_y, grid_z, ticker):
    fig = go.Figure(data=[
        go.Surface(
            x=grid_x,
            y=grid_y,
            z=grid_z,
            colorscale='Viridis',
            opacity=0.9,
            hoverinfo='x+y+z',
            contours={
                'x': {'show': True, 'color': 'white', 'highlightcolor': 'white'},
                'y': {'show': True, 'color': 'white', 'highlightcolor': 'white'},
                'z': {'show': True, 'start': grid_z.min(), 'end': grid_z.max(), 
                      'size': (grid_z.max()-grid_z.min())/10}
            }
        )
    ])
    
    fig.update_layout(
        title=f'Implied Volatility Surface for {ticker}',
        scene={
            'xaxis': {'title': 'Strike Price'},
            'yaxis': {'title': 'Time to Expiry (years)'},
            'zaxis': {'title': 'Implied Volatility'},
            'camera': {'eye': {'x': 1.5, 'y': 1.5, 'z': 0.7}}
        },
        margin={'l': 0, 'r': 0, 'b': 0, 't': 30},
        height=800
    )
    
    fig.update_traces(
        hovertemplate=(
            "<b>Strike:</b> %{x:.2f}<br>"
            "<b>Expiry:</b> %{y:.2f} years<br>"
            "<b>IV:</b> %{z:.2%}<extra></extra>"
        )
    )
    
    return fig

# Main app logic
if generate_btn:
    with st.spinner(f"Generating volatility surface for {ticker}..."):
        try:
            # Get data (replace with actual API call)
            strikes, expiries, iv = get_sample_data(ticker)
            
            # Create interpolation grid
            grid_x, grid_y, grid_z = create_3d_interpolation_grid(
                strikes, expiries, iv, interpolation_method
            )
            
            if grid_x is not None:
                # Create and display plot
                fig = create_plotly_figure(grid_x, grid_y, grid_z, ticker)
                plot_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Show success message
                st.success(f"Volatility surface generated for {ticker}!")
                
        except Exception as e:
            st.error(f"Error generating surface: {str(e)}")

# Initial message when app loads
if not generate_btn:
    with main_container:
        st.markdown("""
        ## Welcome to the Volatility Surface Explorer!
        
        This app visualizes implied volatility surfaces for equity options.
        
        **To get started:**
        1. Enter a ticker symbol (default: SPY)
        2. Select interpolation method
        3. Click "Generate Volatility Surface" button
        """)
        
        st.image("https://quantdare.com/wp-content/uploads/2016/06/volsurface.png", 
                caption="Example Volatility Surface", width=600)