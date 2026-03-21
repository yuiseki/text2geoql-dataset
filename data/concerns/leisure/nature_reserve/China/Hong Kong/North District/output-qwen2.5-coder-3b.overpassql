[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh"~"香港"]->.inner;
(
  nwr["leisure"~"nature_reserve"](area.inner)(area.outer);
);
out geom;
