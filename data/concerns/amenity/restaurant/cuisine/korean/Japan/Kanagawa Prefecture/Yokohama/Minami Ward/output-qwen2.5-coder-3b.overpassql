[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
