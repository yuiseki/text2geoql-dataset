[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
