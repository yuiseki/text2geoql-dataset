[out:json][timeout:30];
area["name:en"="Kobe"]->.outer;
area["name:en"="Hyogo Prefecture"]->.inner;
(
  nwr["cuisine"~"chinese"](area.inner)(area.outer);
);
out geom;
