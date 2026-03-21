[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh-hk"="香港特别行政区"];
(
  nwr["leisure"="fishing"](area.outer);
);
out geom;
