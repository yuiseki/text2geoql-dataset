[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;
