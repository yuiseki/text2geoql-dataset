[out:json][timeout:30];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["leisure"="water_park"](area.inner)(area.outer);
);
out geom;
