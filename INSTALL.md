# Installing NicheTypeR

`NicheTypeR` is currently a prototype R package. Install from GitHub with:

```r
install.packages("remotes")
remotes::install_github("123hzq321/NicheTypeR", upgrade = "never")
```

If you are working from a local source checkout, install from the package
directory with:

```r
remotes::install_local(".", upgrade = "never")
```

For development:

```r
install.packages(c("devtools", "testthat"))
devtools::load_all(".")
devtools::test(".")
```

To build the application-note vignette, install the optional vignette tools:

```r
install.packages(c("knitr", "rmarkdown"))
```

Then run:

```r
devtools::build_vignettes(".")
```

Run package checks in an R-enabled environment before release:

```bash
R CMD check --no-manual --no-build-vignettes .
```
