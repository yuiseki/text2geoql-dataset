[out:json][timeout:30];
area["name:en"="Aichi Prefecture"]->.outer;
area["name:ja"="愛知県"]->.inner;
(
  nwr["leisure"="fishing"](area.inner)(area.outer);
);
out geom;
