[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
