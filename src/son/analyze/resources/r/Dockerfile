FROM rocker/hadleyverse:latest

RUN echo 'to_install <- c("devtools", "roxygen2", "httr", "purrr", "gridExtra", \
                          "rjson", "ggplot2", "forecast", "markovchain", "lubridate", \
                          "zoo", "xts", "som");' >> /tmp/cmds.R \
    && echo 'install.packages(to_install);' >> /tmp/cmds.R \
    && cat /tmp/cmds.R | r - \
    && echo 'Done'

COPY ./examples /home/rstudio/examples
COPY ./son.analyze /var/tmp/son.analyze

RUN echo 'setwd("/var/tmp/son.analyze"); devtools::document(); setwd(".."); devtools::install("son.analyze", build_vignettes =TRUE)' | r - \
    && chown -R 'rstudio:rstudio' /var/tmp/son.analyze

# RUN echo 'setwd("/var/tmp/son.analyze");' >> /etc/R/Rprofile.site \
#     && echo 'devtools::document();' >> /etc/R/Rprofile.site \
#     && echo 'setwd("/home/rstudio");' >> /etc/R/Rprofile.site \
#     && echo 'devtools::load_all("/var/tmp/son.analyze");' >> /etc/R/Rprofile.site
