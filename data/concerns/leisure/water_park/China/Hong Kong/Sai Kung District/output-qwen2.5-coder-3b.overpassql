[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["leisure"~"water_park"](area.outer);
);
out geom;
