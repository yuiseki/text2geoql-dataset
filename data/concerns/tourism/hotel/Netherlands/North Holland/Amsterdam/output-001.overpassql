[out:json][timeout:30];
area["name:en"="North Holland"]->.outer;
area["name:en"="Amsterdam"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;