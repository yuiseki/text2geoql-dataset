[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
