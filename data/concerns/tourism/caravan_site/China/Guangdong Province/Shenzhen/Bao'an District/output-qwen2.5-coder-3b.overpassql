[out:json][timeout:30];
area["name:en"="Guangdong Province"][boundary=administrative]->.outer;
(
  nwr["tourism"="caravan_site"](area.outer);
);
out geom;
