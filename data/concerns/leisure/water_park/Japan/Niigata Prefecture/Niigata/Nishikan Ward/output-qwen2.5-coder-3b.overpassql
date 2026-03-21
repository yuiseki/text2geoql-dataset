[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["leisure"~"water_park"](area.inner)(area.outer);
);
out geom;
