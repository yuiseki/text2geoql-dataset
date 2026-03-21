[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
