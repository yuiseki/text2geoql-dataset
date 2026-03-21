[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["office"~"government"](area.outer);
);
out geom;
