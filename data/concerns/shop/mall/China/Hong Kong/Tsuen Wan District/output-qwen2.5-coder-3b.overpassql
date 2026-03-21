[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
