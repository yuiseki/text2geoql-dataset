[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
