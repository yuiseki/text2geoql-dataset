[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["leisure"~"nature_reserve"](area.outer);
);
out geom;
