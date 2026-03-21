[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh"~"香港"]->.inner;
(
  nwr["leisure"~"playground"](area.inner)(area.outer);
);
out geom;
