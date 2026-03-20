[out:json][timeout:30];
area["name:en"="Kwai Tsing District"][boundary=administrative]->.outer;
(
  nwr["tourism"="attraction"](area.outer);
);
out geom;
