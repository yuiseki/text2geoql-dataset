[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
