
from HelmertTool.interface.MainWindow import MainWindow

if __name__ == '__main__':
    # try:
    #     opts, args = getopt.getopt(sys.argv[1:], "f:t:" , ["from","to"])
    #     print(opts, args)
    # except getopt.GetoptError:
    #     print('Bad arguments')
    #     sys.exit(2)

    # for opt, arg in opts:
    #     if opt == "from":
    #         from_df = load_df(arg[0])
    #     if opt == "to":
    #         to_df = load_df(arg[0]) 

    #GUI
    
    main = MainWindow()
    main.mainloop()
    # from_df = load_sta("C:/Users/Adrian/Documents/NVI/helmert-transformation/data/2020d_off_0_0_10p_rate_0_0_0.sta")
    # to_df = load_sta("C:/Users/Adrian/Documents/NVI/helmert-transformation/data/2020d.sta")
    
    # transform = HelmertTransform(from_df, to_df, weighted = True, type = "9")
    # print(transform)
    
    # fig, (ax1, ax2) = plt.subplots(2,1)
    # transform.plot_residuals(ax1, ax2)
    # plt.show()

    # fig, (ax1, ax2) = plt.subplots(2,1)
    # transform.plot_residuals_hist(ax1, ax2)
    # plt.show()
