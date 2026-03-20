[out:json][timeout:30];
area["name:en"="Guangdong Province"][boundary=administrative]->.outer;
(
  nwr["shop"~"supermarket"](area.outer);
);
out geom;
