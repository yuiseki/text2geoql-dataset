[out:json][timeout:30];
area["name:en"="Atsuta Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
