// Important note: Sushi shops are typically found in traditional Japanese restaurants or sushi bars.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Hachijō"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
