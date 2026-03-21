[out:json][timeout:30];
area["name:en"="Longgang District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["leisure"~"dog_park"](area.inner)(area.outer);
);
out geom;
