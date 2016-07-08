context(makeContextTitle("Utils expectations"))

test_that("version matches", {
  expect_equal(son.analyze::version, "0.0.2")
})

test_that("verify that an empty result returns an empty list", {
  rq <- sonQuery("cnt_cpu_perc{id=~'^___unlikely_id___.+'}")
  expect_warning(fetch("empty_result.json", rq, silent = FALSE))
  x <- fetch("empty_result.json", rq)
  expect_equal(x, list())
})

test_that("verify a basic query", {
  rq <- sonQuery("cnt_cpu_perc{id=~'^93a02b23a.+'}")
  x <- fetch("basic_query_01.json", rq)
  expect_length(x, 1)
  x <- x[[1]]
  expect_equal(x$metricName, "cnt_cpu_perc")
  expect_match(x$id, "93a02")
  expect_gt(length(x$labels), 0)
  expect_true(is.data.frame(x$df))
})
