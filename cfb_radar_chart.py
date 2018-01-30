import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # improves plot aesthetics


def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d-y1) / (y2-y1) 
                     * (x2 - x1) + x1)
    return sdata


class CfbRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=7):
        # creates arra between 0 - 360 of depending on variables
        # i.e. ten variables equals array ten even points between 0 -360
        angles = np.arange(0, 360, 360./len(variables))
        
        # creates axis and adds label. Could also use add_subplot 
        axes = [fig.add_axes([0.1,0.1,0.9,0.9],polar=True,
                label = "axes{}".format(i)) 
                for i in range(len(variables))]
        
        # add frac 1.2 to spaceout label from edge
        l, text = axes[0].set_thetagrids(angles, 
                                         labels=variables,
                                        frac=1.2)
        # set polar chart clockwise
        axes[0].set_theta_direction(-1)
        #sets 0 deg a top of  chart
        axes[0].set_theta_zero_location("N")
        
        """
        # rotates the labels 90 degrees
        [txt.set_rotation(angle-90) for txt, angle 
            in zip(text, angles)]
        """

        for ax in axes[1:]:
            #turns off patch which is 2D artist w/ face color and edge color
            ax.patch.set_visible(False)
            #turn grid highlight off. lets area between points stand out above it
            ax.grid(False)
            # turns off visiblity of  0 - 45 -90 axis
            ax.xaxis.set_visible(False)
        #enumerate adds bound count to loop
        # loop currently is labeling all axes, only need it to lable one.
        for i, ax in enumerate(axes):
            # linspace returns evenly spaced numbers over interval n_ordiated_levels 
            grid = np.linspace(*ranges[i], 
                                   num=n_ordinate_levels)
            if i == 0:                
                # sets label to text and convert to int
                gridlabel = ["{}".format(int(x)) 
                             for x in grid[::-1]]

                ax.set_rgrids(grid, labels=gridlabel,
                              angle=angles[i], horizontalalignment='right',
                              weight='bold', zorder=10)
            else:
                gridlabel = ["" for x in grid[::-1]]
                ax.set_rgrids(grid, angle=angles[i], labels=gridlabel)

            # sets data limits for y-axis. * unpacks list
            ax.set_ylim(*ranges[i])
        
        # add text for different quandrants 
        axes[0].text(-0.1, 0.9, 'Passing', weight='bold',
                     horizontalalignment='right', transform=axes[0].transAxes)
        axes[0].text(-0.1, 0.1, 'Explosiveness', weight='bold',
                     horizontalalignment='right', transform=axes[0].transAxes)
        axes[0].text(1.1, 0.1, 'Rushing', weight='bold',
                     horizontalalignment='left', transform=axes[0].transAxes)
        axes[0].text(1.1, 0.9, 'Efficiency', weight='bold',
                     horizontalalignment='left', transform=axes[0].transAxes)
        
        # variables for plotting
        # deg2rad converst angles from degrees to radians
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


if __name__ == '__main__':
    ############  settings ############
    # base settings
    year = 2017
    team = "Clemson"

    # change base path to save/read files other than current working directory
    base_path = None # change from None if not working with cwd
    cwd = os.getcwd()
    path = cwd if base_path is None else base_path
    
    # excel file name to be uploaded
    excel_file = 'Mock_2017_Clemson_Def.xlsx'
    
    # Is offensive radar chart True or False
    off_radar_chart = False
    radar_chart_type = 'Offense' if off_radar_chart else 'Defense'
    title = '{} {} {} Radar'.format(year, team, radar_chart_type)

    # Team's primary and secondary colors
    primary_color = '#F66733'
    sec_color = '#522D80'
    
    # png file settings
    png_name = '{}_{}_{}_radar.png'.format(year, team.lower(), radar_chart_type.lower())
    # higher number better resolution and bigger file size
    dots_per_inch = 300

    ############  settings ############

    # load in excel file and convert data
    df = pd.read_excel(os.path.join(path,excel_file))
    variables = tuple(df.Metric)
    data = tuple(df.Rank)
    
    # ranges of 121 to 1 cfb ranks
    ranges = [(121, 1), ] * len(variables)

    # line or fill color based on Off or Def
    plot_color = sec_color if off_radar_chart else primary_color
    fill_color = primary_color if off_radar_chart else sec_color

    # plot radar chart
    fig1 = plt.figure(figsize=(6, 6))
    radar = CfbRadar(fig1, variables, ranges)
    plt.title(title, color=fill_color, y=1.15, x=0.01,
            fontdict= {'fontsize': 16, 'fontweight': 'bold'})

    # if offense radar chart primary color = fill color else sec_color = fill color 
    radar.plot(data, color=plot_color, mfc=plot_color, lw=3, alpha=0.5)
    radar.fill(data, alpha=0.5, fc=fill_color, ec=plot_color)
    
    #save chart to file
    plt.savefig(os.path.join(path, png_name), dpi=dots_per_inch, bbox_inches='tight', pad_inches=0.1)
